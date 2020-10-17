#!/usr/bin/env python3
# scan_json.py -- Scan JSON from Legiscan API
# By Tony Pearson, IBM, 2020
#
import base64
import codecs
import json
import os
import re
import sys
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

from cfc_app.ShowProgress import ShowProgress
from cfc_app.PDFtoTEXT import PDFtoTEXT
from cfc_app.models import Location
from cfc_app.Legiscan_API import Legiscan_API
from cfc_app.Oneline import Oneline

PARSER = "lxml"
TITLE_LIMIT_CHARS = 200
SUMMARY_LIMIT_CHARS = 1000

HeadForm = "{} {} _TITLE_ {} _SUMMARY_ {} _TEXT_"


class Command(BaseCommand):
    help = 'For each state, scan the NN.json file, converting '
    help += 'HTML and PDF versions of each legislation into text file'

    def add_arguments(self, parser):
        parser.add_argument("--json", help="Specify single JSON file")
        parser.add_argument("--fresh", action="store_true",
                            help="Invoke Legiscan.com API")
        parser.add_argument("--skip", action="store_true",
                            help="Skip if text file already exists")
        return None

    def handle(self, *args, **options):
        leg = Legiscan_API()

        if options['json']:
            jsf = options['json']
            state = jsf[:2]
            fullname = os.path.join(settings.SOURCE_ROOT, jsf)
            self.process_json(state, fullname, options)
        else:
            usa = Location.objects.get(shortname='usa')
            locations = Location.objects.order_by(
                'hierarchy').filter(parent=usa)
            for loc in locations:
                state = loc.shortname.upper()  # Convert state to UPPER CASE
                fullname = os.path.join(settings.SOURCE_ROOT, state+'.json')
                self.process_json(state, fullname, options)
        return None

    def process_json(self, state, jsonname, options):
        print('project_json', state, jsonname)
        with open(jsonname, "r") as jsonfile:
            data = json.load(jsonfile)
            num = 0
            dot = ShowProgress()
            for entry in data:
                num += 1
                import pdb; pdb.set_trace()
                if num > 10:
                    break
                dot.show()
                bill = data[entry]
                print(bill)

                key = "{}-{}".format(state, bill['bill_number'])
                document_date = ''
                if 'doc_date' in bill:
                    document_date = bill['doc_date']
                    if len(key) < 15:
                        key += '-Y' + bill['doc_date'][:4]
                    else:
                        key += '-Y' + bill['doc_date'][2:4]

                title = self.remove_section_numbers(bill['title'])
                summary = self.remove_section_numbers(bill['summary'])

                if len(title) > TITLE_LIMIT_CHARS:
                    revised = self.shrink_line(title, TITLE_LIMIT_CHARS)

                if len(summary) > SUMMARY_LIMIT_CHARS:
                    revised = self.shrink_line(summary, SUMMARY_LIMIT_CHARS)

                # If the text file already exists, honor the --skip flag
                textname = '{}.{}'.format(key, 'txt')
                text_path = os.path.join(settings.SOURCE_ROOT, textname)
                if options['skip'] and os.path.exists(text_path):
                    continue

                # Don't invoke Legiscan.com API unless --fresh specified
                if options['fresh']:
                    print('FRESH')

                    docID = bill['doc_id']
                    LastDate = bill['doc_date']

                    leg = Legiscan_API()
                    response = leg.getBillText(docID)
                    mime_type = response['mime_type']
                    extension = self.determine_extension(mime_type)

                    mimedata = reponse['doc'].encode('latin-1')
                    msg_bytes = base64.b64decode(mimedata)

                    billname = '{}.{}'.format(key, extension)
                    bill_path = os.join.path(settings.SOURCE_ROOT, billname)

                    if extension == 'html':
                        billtext = msg_bytes.decode('latin-1')
                        with open(bill_path, "w") as billfile:
                            print(billtext, file=billfile)
                    elif extension == 'pdf':
                        with open(bill_path, "wb") as billfile:
                            billfile.write(msg_bytes)

                # Otherwise, read the HTML/PDF from SOURCE_ROOT directory
                else:
                    extension = 'unk'
                    if state == 'AZ':
                        extension = 'html'
                        billname = '{}.{}'.format(key, extension)
                        bill_path = os.path.join(
                            settings.SOURCE_ROOT, billname)
                        if os.path.exists(bill_path):
                            with open(bill_path, "r") as billfile:
                                billtext = billfile.read()
                        else:
                            print('File not found: ', bill_path)
                            continue

                    elif state == 'OH':
                        extension = 'pdf'
                        billname = '{}.{}'.format(key, extension)
                        bill_path = os.path.join(
                            settings.SOURCE_ROOT, billname)
                        if os.path.exists(bill_path):
                            with open(bill_path, "rb") as billfile:
                                msg_bytes = billfile.read()
                        else:
                            print('File not found: ', bill_path)
                            continue

                if extension == 'html':
                    self.process_html(key, document_date,
                                     title, summary, billtext)
                elif extension == 'pdf':
                    self.process_pdf(key, document_date, 
                                    title, summary, msg_bytes)

            dot.end()
        return self

    def parse_html(self, in_line, out_line):
        soup = BeautifulSoup(in_line, PARSER)
        title = soup.find('title')
        if title:
            out_line.add_text(title.string)

        sections = soup.findAll("span", {"class": "SECHEAD"})
        for section in sections:
            rawtext = section.string
            if rawtext:
                lines = rawtext.splitlines()
                header = " ".join(lines)
                out_line.add_text(header)

        paragraphs = soup.findAll("p")
        for paragraph in paragraphs:
            pg = paragraph.string
            if pg:
                out_line.add_text(pg)

        return self

    def process_html(self, key, docdate, title, summary, billtext):
        billname = '{}.{}'.format(key, 'html')
        textname = '{}.{}'.format(key, 'txt')

        text_line = Oneline()
        text_line.path = settings.SOURCE_ROOT
        text_line.add_text(HeadForm.format(billname, docdate, title, summary))
        self.parse_html(billtext, text_line)
        text_line.write_name(textname)
        return self

    def parse_intermediate(self, input_string, output_line):
        lines = input_string.splitlines()
        for line in lines:
            newline = line.replace('B I L L', 'BILL')
            newline = newline.strip()
            # Remove lines that only contain blanks or line numbers only
            if newline != '' and not newline.isdigit():
                output_line.add_text(newline)
        return self

    def process_pdf(self, key, docdate, title, summary, msg_bytes):
        billname = '{}.{}'.format(key, 'pdf')
        bill_path = os.path.join(settings.SOURCE_ROOT, billname)
        intermediate = os.path.join(settings.SOURCE_ROOT, "intermediate.file")
        textname = '{}.{}'.format(key, 'txt')

        PDFtoTEXT(bill_path, intermediate)
        text_line = Oneline()
        text_line.path = settings.SOURCE_ROOT
        text_line.add_text(HeadForm.format(billname, docdate, title, summary))
        with open(intermediate, "r") as infile:
            input_str = infile.read()
            self.parse_intermediate(input_str, text_line)
        text_line.write_name(textname)
        return self

    def remove_section_numbers(self, line):
        newline = re.sub(r'and [-0-9]+[.][0-9]+\b\s*', '', line)
        newline = re.sub(r'\([-0-9]+[.][0-9]+\)[,]?\s*', '', newline)
        newline = re.sub(r'\b[-0-9]+[.][0-9]+\b[,]?\s*', '', newline)
        newline = re.sub(
            r'section[s]? and section[s]?\s*', 'sections', newline)
        newline = re.sub(r'section[s]?\s*;\s*', '; ', newline)
        newline = re.sub(r'amend; to amend,\s*', 'amend ', newline)
        newline = newline.replace("'", " ").replace('"', ' ')
        newline = newline.replace(r'\x91', '')
        return newline

    def shrink_line(self, line, limit):
        newline = re.sub(r'^\W*\w*\W*', '', line[-limit:])
        newline = re.sub(r'^and ', '', newline)
        newline = newline[0].upper() + newline[1:]
        return newline

    def determine_extension(self, mime_type):
        extension = 'unk'
        if mime_type == 'text/html':
            extension = 'html'
        elif mime_type == 'application/pdf':
            extension = 'pdf'
        elif mime_type == 'application/doc':
            extension = 'doc'

        return extension

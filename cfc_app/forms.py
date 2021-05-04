#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cfc_app/forms.py -- Input forms for GUI.

Written by Tony Pearson, IBM, 2020
Licensed under Apache 2.0, see LICENSE for details
"""

# System imports
# Django and other third-party imports
from django import forms
from cfc_app.models import Location, Impact



class SearchForm(forms.Form):
    """ Input form to search legislation """      
    country = forms.ModelChoiceField(
        queryset=Location.objects.filter(govlevel='country'),
        empty_label='Please select a country'
    )

    state = forms.ModelChoiceField(
        empty_label='Select a state (optional)',
        required = False,
        queryset=Location.objects.none()
    )

    county = forms.ModelChoiceField(
        empty_label='Select a county (optional)',
        required = False,
        queryset=Location.objects.none()
    )

    city = forms.ModelChoiceField(
        empty_label='Select a city (optional)',
        required = False,
        queryset=Location.objects.none()
    )

    impacts = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Impact.objects.all().exclude(iname='None')
    )

    def __init__(self, *args, **kwargs):
        """Specify location and impact pull down menus """
        super().__init__(*args, **kwargs)
        self.fields['state'].queryset = Location.objects.none()
        self.fields['county'].queryset = Location.objects.none()
        self.fields['city'].queryset = Location.objects.none()
        
        # For case where criteria is auto-filling
        if 'location' in self.data:
            try:
                location_data = self.data.get('location')
                impacts_data = self.data.get('impacts')
                self.fields['impacts'].initial = impacts_data.all()
                # Moves down hierarchy and decides what lowest possible query can be set to
                if location_data.govlevel == 'country':
                    self.fields['state'].queryset = Location.objects.filter(parent=location_data)
                    self.fields['country'].initial = location_data
                if location_data.govlevel == 'state':
                    self.fields['state'].queryset = Location.objects.filter(parent=location_data.parent)
                    self.fields['county'].queryset = Location.objects.filter(parent=location_data)
                    self.fields['state'].initial = location_data
                if location_data.govlevel == 'county':
                    self.fields['state'].queryset = Location.objects.filter(parent=location_data.parent.parent)
                    self.fields['county'].queryset = Location.objects.filter(parent=location_data.parent)
                    self.fields['city'].queryset = Location.objects.filter(parent=location_data)
                    self.fields['county'].initial = location_data
                if location_data.govlevel == 'city':
                    self.fields['state'].queryset = Location.objects.filter(parent=location_data.parent.parent.parent)
                    self.fields['county'].queryset = Location.objects.filter(parent=location_data.parent.parent)
                    self.fields['city'].queryset = Location.objects.filter(parent=location_data.parent)
                    self.fields['city'].initial = location_data
            except (ValueError, TypeError):
                pass

        # Decides on priority down the list, and fills as much as possible
        elif 'county' in self.data:
            try:
                county_data = self.data.get('county')
                self.fields['city'].queryset = Location.objects.filter(parent=county_data)
                self.fields['county'].queryset = Location.objects.filter(parent=county_data.parent)
                self.fields['state'].queryset = Location.objects.filter(parent=county_data.parent.parent)
                self.fields['county'].initial = county_data
            except (ValueError, TypeError):
                pass

        elif 'state' in self.data:
            try:
                state_data = self.data.get('state')
                self.fields['county'].queryset = Location.objects.filter(parent=state_data)
                self.fields['state'].queryset = Location.objects.filter(parent=state_data.parent)
                self.fields['state'].initial = state_data
            except (ValueError, TypeError):
                pass

        elif 'country' in self.data:
            try:
                country_data = self.data.get('country')
                self.fields['state'].queryset = Location.objects.filter(parent=country_data)
                self.fields['country'].initial = country_data
            except (ValueError, TypeError):
                pass

        # if you want to do just one
        self.fields['country'].error_messages = {
            'required': 'A location must be selected'}
        self.fields['impacts'].error_messages = {
            'required': 'Select one or more impact areas'}

# end of module

from django import forms
import re

class SurveyForm(forms.Form):
  file = forms.FileField(required=True)
  reg_no = forms.CharField(max_length=10, min_length=10, required=True)
  phone_no = forms.CharField(max_length=8, min_length=8, required=True)
  
  def clean_reg_no(self):
      reg_no = self.cleaned_data['reg_no']
      pattern = r'^[А-Яа-яӨөҮү]{2}\d{8}$'
      if not re.match(pattern, reg_no):
          raise forms.ValidationError("Зөв регистэрийн дугаар биш байна.")
      return reg_no

  def clean_phone_no(self):
      phone_no = self.cleaned_data['phone_no']
      pattern = r'^\d{8}$'
      if not re.match(pattern, phone_no):
          raise forms.ValidationError("Зөв утасны дугаар биш байна.")
      return phone_no
  
class SurveySearchForm(forms.Form):
  reg_no = forms.CharField(max_length=10, min_length=10, required=True)
  phone_no = forms.CharField(max_length=8, min_length=8, required=True)
  
  def clean_reg_no(self):
      reg_no = self.cleaned_data['reg_no']
      pattern = r'^[А-Яа-яӨөҮү]{2}\d{8}$'
      if not re.match(pattern, reg_no):
          raise forms.ValidationError("Зөв регистэрийн дугаар биш байна.")
      return reg_no

  def clean_phone_no(self):
      phone_no = self.cleaned_data['phone_no']
      pattern = r'^\d{8}$'
      if not re.match(pattern, phone_no):
          raise forms.ValidationError("Зөв утасны дугаар биш байна.")
      return phone_no



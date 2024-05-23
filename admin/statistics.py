from main.core import utils as core_model
from bacter_identification.models import Survey
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from collections import defaultdict
from authentication.models import MerchantAdmin, MerchantEmployee

current_year = timezone.now().year

def get_all_survey_number():
    surveys = Survey.objects.all()  
    return surveys.__len__

def get_all_user_number():
    users = MerchantAdmin.objects.filter(is_superuser=0)
    return users.__len__

def new_users_monthly():
    #   .annotate(month=ExtractMonth('created_at')) \
    #   .values('month') \
    #   .order_by('month')
    user_stats = MerchantAdmin.objects \
      .filter(created_at__year=current_year, is_superuser=False) \
      .annotate(count=Count('id'))
    new_users_mothly_count = [0] * 12
    
    for item in user_stats:
        month_index = item.created_at.month - 1
        new_users_mothly_count[month_index] = item.count
    
    return new_users_mothly_count

def surveys_monthly(userId=None):
    # .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at')) \
    # .values('year', 'month') \
    # .order_by('year', 'month')

    if userId is None:
        survey_stats = Survey.objects \
            .filter(created_at__year=current_year) \
            .annotate(total_row_number=Sum('rowNumber'), count=Count('id'))
    else:
        survey_stats = Survey.objects \
            .filter(created_at__year=current_year, userId=userId) \
            .annotate(total_row_number=Sum('rowNumber'), count=Count('id'))
    
    monthly_row_count = [0] * 12
    monthly_survey_count = [0] * 12

    for item in survey_stats:
        month_index = item.created_at.month - 1
        monthly_row_count[month_index] = item.total_row_number
        monthly_survey_count[month_index] = item.count

    return monthly_row_count, monthly_survey_count


def result_by_customer(userId):
  surveys = Survey.objects.filter(userId=userId)
  results= []
  for survey in surveys:
    data = core_model.get_file(survey.resultFileName, 'survey-results')
    result_data = core_model.process_result_data(data.values)
    if len(result_data) != 0: 
      results.append(result_data)
  def percent_to_float(s):
    return float(s.strip('%')) / 100

  merged_data = defaultdict(float)
  for d in results:
      for key, value in d.items():
          merged_data[key] += percent_to_float(value)

  total_sum = sum(merged_data.values())

  normalized_data = {k: f"{(v / total_sum) * 100:.4f}%" for k, v in merged_data.items()}

  return normalized_data
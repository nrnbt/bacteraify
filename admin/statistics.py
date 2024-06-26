from core.core import utils as core_model
from bacter_identification.models import Survey
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from collections import defaultdict

current_year = timezone.now().year

def get_all_survey_number():
    surveys = Survey.objects.all()  
    return surveys.__len__

def get_all_user_number():
    users = get_user_model().objects.filter(is_superuser=0)
    return users.__len__

def new_users_monthly():
    user_stats = get_user_model().objects \
      .filter(created_at__year=current_year, is_superuser=False)
    
    new_users_mothly_count = [0] * 12

    for user in user_stats:
        month = user.created_at.month
        new_users_mothly_count[month] += 1
    
    return new_users_mothly_count

def surveys_monthly(userId=None):

    if userId is None:
        survey_stats = Survey.objects \
            .filter(created_at__year=current_year) \
            .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at')) \
            .values('year', 'month') \
            .annotate(total_row_number=Sum('rowNumber'), count=Count('id')) \
            .order_by('year', 'month')
    else:
        survey_stats = Survey.objects \
            .filter(created_at__year=current_year, userId=userId) \
            .annotate(year=ExtractYear('created_at'), month=ExtractMonth('created_at')) \
            .values('year', 'month') \
            .annotate(total_row_number=Sum('rowNumber'), count=Count('id')) \
            .order_by('year', 'month')
    
    monthly_row_count = [0] * 12
    monthly_survey_count = [0] * 12

    for item in survey_stats:
        month_index = item['month'] - 1
        monthly_row_count[month_index] = item['total_row_number']
        monthly_survey_count[month_index] = item['count']

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
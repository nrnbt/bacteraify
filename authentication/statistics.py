from django.utils import timezone
from django.db.models import Count
from datetime import datetime, timedelta
from authentication.models import MerchantEmployee
from bacter_identification.models import Survey, ClassificationResult
from collections import Counter
from main.core.utils import Predictor
from django.db.models.functions import TruncMonth
from main.core.constants import COLORS, STRAINS
from django.db.models import Count
from datetime import datetime, timedelta
from collections import defaultdict

def new_employee_weekly_report(merchant_id):
    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    new_employee_data = (
        MerchantEmployee.objects.filter(
            merchant_id=merchant_id, 
            created_at__gte=start_date,
            created_at__lte=today + timedelta(days=1)
        )
        .extra({'created_at_date': "DATE(created_at)"})
        .values('created_at_date')
        .annotate(new_employee_count=Count('id'))
        .order_by('created_at_date')
    )
    all_dates = [start_date + timedelta(days=i) for i in range(7)]
    counts_dict = {date: 0 for date in all_dates}
    for item in new_employee_data:
        counts_dict[item['created_at_date']] = item['new_employee_count']
    
    report_data = [{'x': date.strftime('%b %d'), 'y': counts_dict[date]} for date in all_dates]
    return report_data

def survey_weekly_report(merch_id):
    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    new_employee_data = (
        Survey.objects.filter(
            merch_id=merch_id, 
            created_at__gte=start_date,
            created_at__lte=today + timedelta(days=1)
        )
        .extra(select={'created_at_date': "DATE(created_at)"})
        .values('created_at_date')
        .annotate(survey_weekly_count=Count('id'))
        .order_by('created_at_date')
    )
    all_dates = [start_date + timedelta(days=i) for i in range(7)]
    counts_dict = {date: 0 for date in all_dates}
    for item in new_employee_data:
        counts_dict[item['created_at_date']] = item['survey_weekly_count']
    
    report_data = [{'x': date.strftime('%b %d'), 'y': counts_dict[date]} for date in all_dates]
    return report_data

def most_identified_bacterias(merch_id):
    survey_records = Survey.objects.filter(merch_id=merch_id).values('surveyFileName', 'modelTypes', 'status', 'cnnPredFileName', 'svmPredFileName', 'rnnPredFileName')
    survey_results = []
    print('---------------> ', survey['cnnPredFileName'], survey['svmPredFileName'])
    for survey in survey_records:
        model_types = survey['modelTypes']
        predictor = Predictor()
        result_data = predictor.survey_result_data_from_s3(
            model_types=model_types,
            cnn=survey['cnnPredFileName'],
            svm=survey['svmPredFileName'],
            rnn=survey['rnnPredFileName']
        )
        result_by_percentage = predictor.process_prediction_result(result_data)
        survey_results.append(result_by_percentage)

    highest_identified_bacterias = []

    for data in survey_results:
        max_percentage = 0
        max_bacteria = ''
        for entry in data[0]['data']:
            for key, value in entry.items():
                if '%' in value:
                    percentage = float(value.replace('%', ''))
                    if percentage > max_percentage:
                        max_percentage = percentage
                        max_bacteria = entry['bacteria']
        highest_identified_bacterias.append(max_bacteria)

    return highest_identified_bacterias

def most_common_4_string(arr):
    counts = Counter(arr)
    most_common = counts.most_common(4)
    most_repeated = [elem for elem, count in most_common]
    return most_repeated

def total_employee(merchant_id):
    employee = MerchantEmployee.objects.filter(
            merchant_id=merchant_id, 
        )
    return len(employee)

def total_survey(merch_id):
    surveys = Survey.objects.filter(
            merch_id=merch_id, 
        )
    return len(surveys)

def bacteria_monthly(merch_id):
    today = datetime.now()
    last_year = today - timedelta(days=365)
    
    # Initialize lists to store series data and categories
    series = []
    categories = []

    # Iterate over each month of the last year
    current_date = last_year
    while current_date <= today:
        year_month = current_date.strftime("%Y-%m")
        categories.append(current_date.strftime("%d %b"))
        
        # Filter records for the current month
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_records = ClassificationResult.objects.filter(merch_id=merch_id, created_at__gte=month_start, created_at__lte=month_end)
        
        # Initialize counts for current month
        month_counts = defaultdict(int)
        
        # Iterate over records for the current month
        for record in month_records:
            cnn_result = record.cnn_result
            svm_result = record.svm_result
            cnn_bacteria = max(cnn_result, key=lambda x: float(cnn_result[x].strip('%')), default=None)
            svm_bacteria = max(svm_result, key=lambda x: float(svm_result[x].strip('%')), default=None)
            highest_percentage_bacteria = cnn_bacteria if float(cnn_result.get(cnn_bacteria, '0').strip('%')) > float(svm_result.get(svm_bacteria, '0').strip('%')) else svm_bacteria
            if highest_percentage_bacteria:
                month_counts[highest_percentage_bacteria] += 1
        
        # Append data for each bacteria to the series list
        for bacteria_name in STRAINS.values():
            data = month_counts[bacteria_name]
            # Find existing series for the bacteria or create a new one
            bacteria_series = next((s for s in series if s['name'] == bacteria_name), None)
            if bacteria_series:
                bacteria_series['data'].append(data)
            else:
                series.append({
                    'name': bacteria_name,
                    'data': [data],
                    'color': COLORS[len(series) % len(COLORS)]  # Use colors from the COLORS list
                })
        
        # Move to next month
        current_date = current_date + timedelta(days=32)
        current_date = current_date.replace(day=1)
    
    return {'series': series, 'categories': categories[::-1]}




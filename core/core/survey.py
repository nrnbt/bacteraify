from bacter_identification.models import Survey

def survey_result_available(survey_file_name):
    survey = Survey.objects.get(
        surveyFileName=survey_file_name
    )
    return survey.resultFileName

def save_survey(user_id, user_email, file_name, data_len, userHash):
    survey_record = Survey(
        userId = user_id,
        userEmail = user_email,
        surveyFileName = file_name,
        rowNumber = data_len,
        type = 'created',
        userHash = userHash
    )
    survey_record.save()

def update_survey(survey_file_name, result_file_name):
    survey = Survey.objects.get(surveyFileName=survey_file_name)
    survey.resultFileName = result_file_name
    survey.type = 'predicted'
    survey.save()

def filter_survey_by_hash(hash):
    return Survey.objects.filter(userHash=hash)

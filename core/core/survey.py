from bacter_identification.models import Survey

def survey_result_available(s):
    s = s.replace(" predicted", "")
    numbers = s.split("/")
    if len(numbers) == 2 and numbers[0].strip() == numbers[1].strip():
        return True
    else:
        return False

def create_survey(user_id, user_email, file_name, data_len, patient_hash, model_types):
    survey_record = Survey(
        userId = user_id,
        userEmail = user_email,
        surveyFileName = file_name,
        rowNumber = data_len,
        status = 'created',
        patientHash = patient_hash,
        modelTypes = model_types
    )
    survey_record.save()
    return survey_record.id

def update_survey_cnn(survey_file_name, status, file_name):
    survey = Survey.objects.get(surveyFileName=survey_file_name)
    survey.cnnPredFileName = file_name
    survey.status = status
    survey.save()

def update_survey_svm(survey_file_name, status, file_name):
    survey = Survey.objects.get(surveyFileName=survey_file_name)
    survey.svmPredFileName = file_name
    survey.status = status
    survey.save()

def update_survey_rnn(survey_file_name, status, file_name):
    survey = Survey.objects.get(surveyFileName=survey_file_name)
    survey.rnnPredFileName = file_name
    survey.status = status
    survey.save()



def filter_survey_by_hash(hash):
    return Survey.objects.filter(patientHash=hash)

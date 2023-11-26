from django.db import migrations
import numpy as np
from core.core.constants import STRAINS
import json
import os

def insert_data(apps, schema_editor):
    Bacteria = apps.get_model('bacter_identification', 'Bacteria')
    odel_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migrations', 'bacteria_spectrums.npy')

    data = np.load(odel_file_path)

    if data.shape[0] != len(STRAINS):
        raise ValueError("The number of labels does not match the number of samples")
    
    for i, sample in enumerate(data):
        serialized_sample = json.dumps(sample.tolist())

        bacteria_instance = Bacteria(label=STRAINS[i], spectrum=serialized_sample)
        bacteria_instance.save()

class Migration(migrations.Migration):

    dependencies = [
        ('bacter_identification', '0005_bacteria'),
    ]

    operations = [
        migrations.RunPython(insert_data),
    ]

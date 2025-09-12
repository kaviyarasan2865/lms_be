from django.core.management.base import BaseCommand
from accounts.models import College, Subject

class Command(BaseCommand):
    help = 'Populate default NEET PG subjects for all colleges'

    def handle(self, *args, **options):
        # Default NEET PG subjects
        neet_subjects = [
            'Anatomy',
            'Physiology', 
            'Biochemistry',
            'Pathology',
            'Pharmacology',
            'Microbiology',
            'Forensic Medicine',
            'Community Medicine',
            'Medicine',
            'Surgery',
            'Obstetrics & Gynaecology',
            'Paediatrics',
            'Orthopaedics',
            'Ophthalmology',
            'ENT',
            'Dermatology',
            'Psychiatry',
            'Anaesthesia',
            'Radiology',
            'Emergency Medicine'
        ]

        colleges = College.objects.all()
        
        if not colleges.exists():
            self.stdout.write(
                self.style.WARNING('No colleges found. Please create colleges first.')
            )
            return

        total_created = 0
        
        for college in colleges:
            self.stdout.write(f'Processing college: {college.name}')
            
            for subject_name in neet_subjects:
                subject, created = Subject.objects.get_or_create(
                    college=college,
                    name=subject_name,
                    defaults={
                        'code': f'{subject_name[:3].upper()}001',
                        'description': f'{subject_name} for NEET PG preparation',
                        'is_active': True
                    }
                )
                
                if created:
                    total_created += 1
                    self.stdout.write(f'  Created subject: {subject_name}')
                else:
                    self.stdout.write(f'  Subject already exists: {subject_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_created} subjects across {colleges.count()} colleges.')
        )

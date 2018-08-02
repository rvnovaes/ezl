from django.core.management.base import BaseCommand

import luigi


class Command(BaseCommand):
    help = 'Execute ETL suit'

    def add_arguments(self, parser):
        parser.add_argument('etl', choices=['user', 'ecm', 'luigi', 'folder', 'person', 'organ', 
                                            'court_division', 'instance', 'lawsuit', 'movement', 
                                            'task', 'contact_mechanism', 'address', 'cost_center', 
                                            'type_movement'])

    def run_user_etl(self):
        from etl.advwin_ezl.account.user import UserETL
        UserETL().import_data()

    def run_court_division_etl(self):
        from etl.advwin_ezl.law_suit.court_division import CourtDivisionETL
        CourtDivisionETL().import_data()

    def run_instance_etl(self):
        from etl.advwin_ezl.law_suit.instance import InstanceETL
        InstanceETL().import_data()

    def run_contact_mechanism_etl(self):
        from etl.advwin_ezl.core.contact_mechanism import ContactMechanismETL
        ContactMechanismETL().import_data()

    def run_address_etl(self):
        from etl.advwin_ezl.core.address import AddressETL
        AddressETL().import_data()        

    def run_cost_center_etl(self):
        from etl.advwin_ezl.financial.cost_center import CostCenterETL
        CostCenterETL().import_data()        

    def run_person_etl(self):
        from etl.advwin_ezl.core.person import PersonETL
        PersonETL().import_data()

    def run_organ_etl(self):
        from etl.advwin_ezl.law_suit.organ import OrganETL
        OrganETL().import_data()

    def run_folder_etl(self):
        from etl.advwin_ezl.law_suit.folder import FolderETL
        FolderETL().import_data()

    def run_lawsuit_etl(self):
        from etl.advwin_ezl.law_suit.law_suit import LawsuitETL
        LawsuitETL().import_data()

    def run_type_movement_etl(self):
        from etl.advwin_ezl.law_suit.type_movement import TypeMovementETL
        TypeMovementETL().import_data()

    def run_movement_etl(self):
        from etl.advwin_ezl.law_suit.movement import MovementETL
        MovementETL().import_data()

    def run_task_etl(self):
        from etl.advwin_ezl.task.task import TaskETL
        TaskETL().import_data()

    def run_ecm_etl(self):
        from etl.advwin_ezl.task.ecm_task import EcmEtl
        EcmEtl().import_data()

    def run_luigi(self):
        from etl.advwin_ezl.luigi_jobs import EcmTask
        luigi.build([EcmTask()])

    def handle(self, *args, **options):
        etl = options['etl']
        options = {
            'user': self.run_user_etl,
            'court_division': self.run_court_division_etl,
            'instance': self.run_instance_etl,
            'person': self.run_person_etl,
            'organ': self.run_organ_etl,
            'contact_mechanism': self.run_contact_mechanism_etl,
            'address': self.run_address_etl,
            'cost_center': self.run_cost_center_etl,
            'folder': self.run_folder_etl,
            'lawsuit': self.run_lawsuit_etl,
            'type_movement': self.run_type_movement_etl,
            'movement': self.run_movement_etl,
            'task': self.run_task_etl,            
            'ecm': self.run_ecm_etl,
            'luigi': self.run_luigi
        }
        options.get(etl)()

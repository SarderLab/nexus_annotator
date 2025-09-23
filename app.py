import os


from src.fusion_tools.visualization import Visualization
from src.fusion_tools.handler.dsa_handler import DSAHandler
from src.fusion_tools.components import SlideMap, FeatureAnnotation
from src.fusion_tools.database.core import initialize_database
from src.fusion_tools.utils.types import TaskIdentifiers, UserCollectionAccessLevel

COL1 = 'col1'
COL2 = 'col2'
COL3 = 'col3'

dn_feature_schema = {
    'labels':[
        {
            'name': 'Mesangial Expansion',
            'type': 'checkbox',
            'options': [
                'Yes',
            ],
            'order': COL1
        },
        {
            'name': 'Mesangial Hypercellularity',
            'type': 'checkbox',
            'options': [
                'Yes',
            ],
            'order': COL2
        },
        {
            'name': 'Microaneurysm',
            'type': 'checkbox',
            'options': [
                'Cellular',
                'Acellular'
            ],
            'order': COL1
        },
         {
            'name': 'Nodules',
            'type': 'checkbox',
            'options': [
                'Cellular',
                'Paucicellular'
            ],
            'order': COL1
        },
        {
            'name': 'Capillary wall thickening',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Glomerular Hylanosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Not a glom?',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Has Artifact?',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Periglomerular Fibrosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Capsular Drops',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Neovascularization',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Immune cells',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Global Sclerosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Histologically Unremarkable',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Abnormal/Not DN',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Comments',
            'type': 'textarea',
            'placeholder': "Additional comments...",
            'order': COL3
        }
    ]
}


fsgs = {
    'labels':[
        {
            'name': 'Segmental sclerosis',
            'type': 'radio',
            'options': [
                'Present, FSGS',
                'Abnormal, not FSGS'
            ],
            'order': COL1
        },
        {
            'name': 'FSGS',
            'type': 'radio',
            'options': [
                "Perihilar",
                "Collapsing",
                "NOS",
                "Tip lesion"
            ],
            'order': COL2
        },
        {
            'name': 'Hyalinosis',
            'type': 'checkbox',
            'options': [
                'Yes',
            ],
            'order': COL1
        },
        {
            'name': 'Foam cells',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Podocyte capping',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Adhesion to Bowman\'s capsule',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Global Sclerosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Periglomerular Fibrosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Histologically Unremarkable',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Not a Glom?',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Has Artifact?',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': "Suboptimal for interpretation",
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL3
        },
        {
            'name': 'Additional Comments',
            'type': 'textarea',
            'placeholder': "Enter comments...",
            'order': COL3
        }
    ]
}

tx_schema = {
    'labels': [
        {
            'name': 'Not Evaluable',
            'type': 'checkbox',
            'options': [
                'Capsule'
            ],
            'order': COL1
        },
        {
            'name': 'Normal',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Medulla',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL1
        },
        {
            'name': 'Glomerulus',
            'type': 'checkbox',
            'options': [
                'Sclerosed',
                'Ischemic',
                'PGF(Periglomerular Fibrosis)',
                'Other Abnormalities'
            ],
            'order': COL1
        },
        {
            'name': 'Artery',
            'type': 'checkbox',
            'options': [
                'Present',
                'Intimal Thickening',
                'Adventitia',
                'Suboptimal'
            ],
            'order': COL1
        },
        {
            'name': 'Tubular Atrophy',
            'type': 'checkbox',
            'options': [
                'Classic',
                'Thyroidization',
                'Endocrinization',
            ],
            'order': COL2
        },
        {
            'name': 'Tubular Basement Membrane',
            "type": "checkbox",
            'options': [
                "Thickening",
                "MultiLayering/Wrinkling",
            ],
            'order': COL2
        },
        {
            'name': 'Interstitial Expansion',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Inflammation',
            'type': 'checkbox',
            'options': [
                'Yes'
            ],
            'order': COL2
        },
        {
            'name': 'Vascular Hylanosis',
            'type': 'radio',
            'options': [
                'Present',
                'Absent (Vessel Present)'
            ],
            'order': COL2
        },
        
        {
            'name': 'Additional Comments',
            'type': 'textarea',
            'placeholder': "Enter comments...",
            'order': COL2
        }
    ]
}

def main():
    os.environ["DATABASE_PATH"] = os.getenv('DATABASE_PATH', '/pubapps/athena/fstools/db' )
    # os.environ["DATABASE_PATH"] = os.getcwd()
    dsa_path = os.getenv('DSA_URL', 'https://athena.rc.ufl.edu/api/v1')
    app_port = 8050 
    dsa_handler = DSAHandler(girderApiUrl=dsa_path)
    task_identifiers: TaskIdentifiers = {
        'FSGS': 'FSGS',
        'DN': 'DN',
        'TX': 'TX'
    }
    
    access_level_def: UserCollectionAccessLevel = {
    "ONLY_USER_FOLDER": "ONLY_USER_FOLDER",
    "ALL_USER_FOLDERS": "ALL_USER_FOLDERS"
    }
    initialize_database()
    vis_session = Visualization(
        linkage = 'page',
        components = {
            "DN Labels": [
                        [
                        (   SlideMap(task_identifier=task_identifiers['DN']),
                            {'width': '3',} 
                        ),
                        (
                            [
                                FeatureAnnotation(
                                    preset_schema=dn_feature_schema,
                                    annotations_format='rgb',
                                    labels_format='json',
                                    storage_path=os.getenv('STORAGE_PATH','/pubapps/athena/fstools/localannotations/dn/'),
                                    # storage_path=os.getcwd(),
                                    task_identifier=task_identifiers['DN']
                                )
                            ],
                            {'width': '9'}
                        )
                        ]
                 ], 
            "Dataset Builder": [
                dsa_handler.create_dataset_builder(access_level=access_level_def["ONLY_USER_FOLDER"])
            ],
            "FSGS Annotation": [
                [
                        (   SlideMap(task_identifier=task_identifiers['FSGS']),
                            {'width': '3'} 
                        ),
                        (
                            [
                                FeatureAnnotation(
                                    preset_schema=fsgs,
                                    annotations_format='rgb',
                                    labels_format='json',
                                    storage_path=os.getenv('STORAGE_PATH','/pubapps/athena/fstools/localannotations/fsgs/'),
                                    # storage_path=os.getcwd(),
                                    task_identifier=task_identifiers['FSGS']
                                )
                            ],
                            {'width': '9'}
                        )
                        ]
            ],
            "Tx Annotation": [
                [
                        (   SlideMap(task_identifier=task_identifiers['TX']),
                            {'width': '4'} 
                        ),
                        (
                            [
                                FeatureAnnotation(
                                    preset_schema=tx_schema,
                                    annotations_format='rgb',
                                    labels_format='json',
                                    storage_path=os.getenv('STORAGE_PATH','/pubapps/athena/fstools/localannotations/tx/'),
                                    # storage_path=os.getcwd(),
                                    task_identifier=task_identifiers['TX']
                                )
                            ],
                            {'width': '8'}
                        )
                        ]
            ],
        },
        header = [
            dsa_handler.create_login_component()
        ],
        app_options = {
            "host": "0.0.0.0",
            "port": int(app_port)
        }
    )
    
    vis_session.start()

if __name__=='__main__':
    main()
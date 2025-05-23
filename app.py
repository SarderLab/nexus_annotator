import os


from src.fusion_tools.visualization import Visualization
from src.fusion_tools.handler.dsa_handler import DSAHandler
from src.fusion_tools.components import SlideMap, FeatureAnnotation
from src.fusion_tools.fusion.data_types import get_upload_types
from src.fusion_tools.database.core import initialize_database


dn_feature_schema = {
    'labels':[
        {
            'name': 'Mesangial Expansion',
            'type': 'radio',
            'options': [
                'Yes',
                'No',
            ]
        },
        {
            'name': '+ Nodules',
            'type': 'radio',
            'options': [
                'Yes',
                'No',
            ]
        },
        {
            'name': 'Microaneurysm',
            'type': 'radio',
            'options': [
                'Yes',
                'No',
            ]
        },
        {
            'name': 'Periglomerular Fibrosis',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'Mesangial Hypercellularity',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'Glomerular Hylanosis',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'Capsular Drops',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'GBM Thickening',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'Neovascularization',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        },
        {
            'name': 'Immune Cells',
            'type': 'radio',
            'options': [
                'Yes',
                'No'
            ]
        }
    ]
}

def main():
    os.environ["DATABASE_PATH"] = os.getcwd()
    dsa_path = 'https://athena.rc.ufl.edu/api/v1'
    app_port = 8050 
    dsa_handler = DSAHandler(girderApiUrl=dsa_path)
    initialize_database()
    vis_session = Visualization(
        linkage = 'page',
        components = {
            "DN Labels": [
                        [
                        (   SlideMap(),
                            {'width': '4',} 
                        ),
                        (
                            [
                                FeatureAnnotation(
                                    preset_schema=dn_feature_schema,
                                    annotations_format='rgb',
                                    labels_format='json',
                                    storage_path=os.getcwd(),
                                )
                            ],
                            {'width': '8'}
                        )
                        ]
                 ], 
            "Dataset Builder": [
                dsa_handler.create_dataset_builder()
            ],
            "Dataset Uploader": [
                dsa_handler.create_uploader(upload_types = get_upload_types())
            ]
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
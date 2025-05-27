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
            'type': 'checkbox',
            'options': [
                'Yes',
            ]
        },
        {
            'name': '+ Nodules',
            'type': 'checkbox',
            'options': [
                'Yes',
            ]
        },
        {
            'name': 'Microaneurysm',
            'type': 'checkbox',
            'options': [
                'Yes',
            ]
        },
        {
            'name': 'Periglomerular Fibrosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'Mesangial Hypercellularity',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'Glomerular Hylanosis',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'Capsular Drops',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'GBM Thickening',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'Neovascularization',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        },
        {
            'name': 'Immune Cells',
            'type': 'checkbox',
            'options': [
                'Yes'
            ]
        }
    ]
}

def main():
    os.environ["DATABASE_PATH"] = os.getenv('DATABASE_PATH', '/pubapps/athena/fstools/db/' )
    dsa_path = os.getenv('DSA_URL', 'https://athena.rc.ufl.edu/api/v1')
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
                                    storage_path=os.getenv('STORAGE_PATH','/pubapps/athena/fstools/localannotations/'),
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
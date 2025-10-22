# *Nexus Annotator*
*A Pathologist-Focused Cloud-ready Platform for AI-Assisted Ground-Truth Generation*

---

## 🚀 Overview  

**Nexus Annotator** is a **cloud-first digital annotation platform** purpose-built for computational pathology workflows.  
Designed in collaboration with pathologists, it streamlines **ground-truth dataset generation** by integrating **AI-assisted region pre-selection**, **consensus-driven labeling**, and **customizable schema definitions** for diverse renal disease cohorts.

Unlike traditional desktop tools that require complex installation, Nexus Annotator operates entirely in the **browser**, providing a scalable, collaborative environment for multi-institutional use.  
It integrates with the **Computational Renal Pathology Suite (CompRePS)** to leverage open-source ML models for pre-identifying regions of interest (ROIs), enabling experts to focus on annotation quality rather than manual navigation.

The platform is currently being used to generate datasets for **Focal Segmental Glomerulosclerosis (FSGS)**, **Diabetic Nephropathy (DN)** and **Transplant (TX)** cohorts.

---

## 🧩 Core Architecture  

### Main Entrypoint — `app.py`  
The `app.py` file is the central entrypoint for the application.  
All new **components to be added**, **pages**, and **cohort schemas** are defined here.

**Main things that operate here include:**
- Adding new disease cohort data schemas and new application components  
- Managing schema definitions and storage paths and database initializations. 
- Integrating each annotation page under the `Visualization` class’s component dictionary  

---

### Application Structure  

All visualization and annotation modules are configured under the `Visualization` class as a `components` dictionary.  
Each unique `key:value` pair under `components` represents an independent **page** in the Nexus Annotator application.

#### Example Configuration for a page
```python
"DN Labels": [
    [
        (
            SlideMap(task_identifier=task_identifiers['DN']),
            {'width': '3'}
        ),
        (
            [
                FeatureAnnotation(
                    preset_schema=dn_feature_schema,
                    annotations_format='rgb',
                    labels_format='json',
                    storage_path=os.getenv('STORAGE_PATH','/pubapps/athena/fstools/localannotations/dn/'),
                    task_identifier=task_identifiers['DN']
                )
            ],
            {'width': '9'}
        )
    ]
]
```

This configuration defines a “DN Labels” page with:

A WSI viewer (SlideMap component) occupying 3 of 12 UI grid columns

A FeatureAnnotation panel occupying the remaining 9 columns

A data scheme (described below) and task identifier tied to the Diabetic Nephropathy cohort to uniquely identify the dataset and isolate them in the database.

## 🧬 Schema Design

Schemas define the annotation structure, field types, and layout for each cohort. A schema specifies what identifiers is collected and how it appears in the UI.

Example Schema

```json
{
    "labels": [
        {
            "name": "Microaneurysm",
            "type": "checkbox",
            "options": ["Cellular", "Acellular"],
            "order": "COL1"
        }
    ]
}
```

## 📋 Supported Field Types

| Type      | Description                          |
|------------|--------------------------------------|
| `checkbox` | Multiple selectable options          |
| `radio`    | Mutually exclusive selection         |
| `text`     | Single-line input                    |
| `textarea` | Multi-line comments or observations  |

---

## 🧱 Layout & Column Control

- Supports **two-column** or **three-column** layouts  
- Column placement via `COL1`, `COL2`, `COL3`  
- If unspecified, defaults to a **two-column evenly split layout**

---

## 🧠 UI and Layout System

**Nexus Annotator** uses a **12-column responsive layout system** inspired by modern web design frameworks.

Each UI component is defined as a tuple:

```python
(component, {'width': '<number_of_columns>'})
SlideMap: { 'width': '3' }
FeatureAnnotation: { 'width': '9' }
```

This ensures flexible, pixel-perfect layouts that scale across devices and resolutions.

## 🔐 Access Control

Access control is handled within the Dataset Builder component through two defined modes:

```
python
access_level_def: UserCollectionAccessLevel = {
    "ONLY_USER_FOLDER": "ONLY_USER_FOLDER",
    "ALL_USER_FOLDERS": "ALL_USER_FOLDERS"
}
```

| Mode      | Description                          |
|------------|--------------------------------------|
| `ONLY_USER_FOLDER` | Displays only data in the user’s folder          |
| `ALL_USER_FOLDERS` | Shows all accessible datasets (for admins or reviewers)         |

This structure ensures appropriate data visibility across users, institutions, and collaborative research groups.

## 🗄 Database and Data Persistence

Nexus Annotator includes a database integration layer that ensures:

- Persistent data across sessions

- Secure storage of all annotations, metadata, and schemas

- Synchronized progress tracking across users

- Each annotation event is logged and versioned to maintain dataset integrity for downstream AI training and validation.

## 🧰 Platform Features

### 🔑 1. Login & Authentication

- Authentication is managed through the connected Digital Slide Archive (DSA) instance (e.g., Athena).

- Users must be registered and approved in DSA to access Nexus Annotator.

### 🧾 2. Data Management

- Datasets are managed through the DSA.

- Users are currently required to maintain personal folders specific to the disease cohort in the user folder for efficient data organization.

### 🧩 3. Annotation Pages

- Each data cohort `(e.g., DN, FSGS)` corresponds to a dedicated annotation page.

- Page definitions and schemas are configured in `app.py`.

### 🧮 4. Annotation Filters

- Annotation files can be filtered by dataset type or annotation criteria.

- Filtering logic is implemented in segmentation.py within the components folder.

- Annotation file names must match those in Athena for synchronization.

### 📊 5. Progress Tracking

Two levels of progress indicators are built in:

| Level      | Description                          |
|------------|--------------------------------------|
| `Slide-level tracking` | Reflects completion percentage for all required annotation files for a given slide          |
| `File-level tracking` | Displays `(completed annotations) / (total annotations)` for each file        |

Progress values auto-refresh every `10 seconds (configurable)`.

### 🧭 6. Intelligent Navigation

- “Next” and “Previous” buttons to traverse ROIs

- Direct jump input for ROI index navigation

- The WSI viewer automatically follows the selected ROI

### 🧾 7. Label Submission

- After completing all ROI annotations for a file, users must click Submit Labels to finalize and export the data for downstream modeling workflows.

### 🧍 8. Reference Image Panel (Optional)

- A dedicated panel can display exemplar reference images to align annotators’ understanding and reduce inter-observer variability.

### ⚙️ Deployment Notes

Deployment is already setup and nothing needs to be modified except for a few environment variables that needs to be switched. Ensure that 

- All storage paths in `FeatureAnnotation` components are correctly mounted

- Environment variable `STORAGE_PATH` is configured in the runtime environment

- File system permissions allow read/write access to annotation directories

Example: 

```
bash
export STORAGE_PATH=/pubapps/athena/fstools/localannotations/dn/
```

Take a copy of the existing db file into the `backup` folder before every deployment and maintian version with different `Docker tags` to easily revert back to the previous stable application version. 

### 🧩 Sample Development Workflow for new additions

Create a new schema for the desired cohort in app.py (can be separated to a different file). 

Register the schema in app.py under the `Visualization` class

Define the page layout components avialble under the `Visualization` class

Specify `task_identifiers` for dataset separation and database addition. 

Run locally and verify:

- UI rendering

- Schema mapping

- Database operations



## License
`nexus annotator` was created by Suhas Katari Chaluva Kumar. It is licensed under the terms of the Apache 2.0 License


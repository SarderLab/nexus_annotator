from typing import TypedDict, Literal

class TaskIdentifiers(TypedDict, total=False):
    FSGS: Literal["FSGS"]
    DN: Literal["DN"]
    
class UserCollectionAccessLevel(TypedDict, total=False):
    """This is used to specify the accesslevel for the dataset builder class. 
    ONLY_USER_FOLDER: This option enables the user to see only the Folders under the "USER" tab in a DSA instance.
    ALL_USER_FOLDER: This option enables the user to see all the collections they have access to on the DSA instance that FUSION is connected to. 
    
    Args:
        TypedDict (_type_): Used to define literals for the access levels to be reused throughout the application. 
        total (bool, optional): This specifies if all the variables should be defined where the Type is used. Defaults to False.
    """
    ONLY_USER_FOLDER: Literal["ONLY_USER_FOLDER"]
    ALL_USER_FOLDERS: Literal["ALL_USER_FOLDERS"]


    
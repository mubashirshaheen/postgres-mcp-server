"""This module contains a specific prompt"""
specific_prompt = (
    """## Relation Between tables:
    Product -> Release -> release_images -> image_permits -> permit -> component
    ## Important:
    - if user prompt is related to get product and component state is ACTION_REQUIRED then
    Add New Column named Link in the table at the end value 'https://tpscompliancedev.cisco.com/compliance/product-releases/product/{product_id}' 


    """
)

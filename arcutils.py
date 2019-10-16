# -*- coding: utf-8 -*-

import os
# import pandas as pd

from access_arcpy import append_arc32_paths
append_arc32_paths()

import arcpy
import logging

#def arcgis_table_to_df(in_fc, input_fields=None, query=""):
#    """Function will convert an arcgis table into a pandas dataframe with an
#    object ID index, and the selected input fields using an
#    arcpy.da.SearchCursor."""
#    
#    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
#    
#    if input_fields:
#        final_fields = [OIDFieldName] + input_fields
#    else:
#        final_fields = [field.name for field in arcpy.ListFields(in_fc)]
#        
#    data = [row for row in arcpy.da.SearchCursor(
#            in_fc, final_fields, where_clause=query)]
#    
#    fc_dataframe = pd.DataFrame(data, columns=final_fields)
#    fc_dataframe = fc_dataframe.set_index(OIDFieldName, drop=True)
#    
#    return fc_dataframe

def get_unused_scratch_fc(fc_name = "next_fc"):
    """Given a name, will return the next empty feature class within the scratch
    geodatabase, appending an incrementing counter to the end until a non-existant
    feature class location is found.

    Args:
        fc_name (str): the desired name of the feature class

    Returns:
        scratch_path (str): the full path in the scratch geodatabase to the next
            non-existent fcnameX feature class.
    """

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    count = 0
    temp_fc = arcpy.env.scratchGDB + os.path.sep + fc_name

    while (arcpy.Exists(temp_fc)):
        temp_fc = arcpy.env.scratchGDB + os.path.sep + fc_name + str(count)
        count = count + 1

    logger.info("New fc created at " + temp_fc)

    return temp_fc

def get_sr_by_fc(fc):
    """This retrieves a spatial reference object by its factory code. Per a
        relevant gis stack exchange,
        
        > If an Esri well-known ID is below 32767, it corresponds to the EPSG
        > ID. WKIDs that are 32767 or above are Esri-defined. Either the object
        > isn't in the EPSG Geodetic Parameter Dataset yet, or it probably
        > won't be added. If an object is later added to the EPSG Dataset, Esri
        > will update the WKID to match the EPSG one, but the previous value
        > will still work.
        
        It should therefore be sufficient to pass the EPSG without worry.

    Args:
        fc (int): An integer representing the spatial reference's factory code.

    Returns:
        an arcpy SpatialReference object for corresponding factory code.
    """
    sr = arcpy.SpatialReference(fc)
    return sr


def get_sr_nad83_gcs():
    """Returns the spatial reference for NAD83 GCS (unprojected).

    Returns:
        an arcpy SpatialReference object for NAD83 GCS (unprojected).
    """
    sr = get_sr_by_fc(4269)
    return sr

def get_sr_nad83_rispf():
    """Returns the spatial reference for NAD83 Rhode Island State Plane Feet.

    Returns:
        an arcpy SpatialReference object for NAD83 Rhode Island State Plane Feet.
    """
    sr = get_sr_by_fc(3438)
    return sr

def get_sr_nad83_utm_z19():
    """Returns the spatial reference for NAD83 UTM Zone 19.

    Returns:
        an arcpy SpatialReference object for NAD83 UTM Zone 19.
    """
    sr = get_sr_by_fc(26919)
    return sr

def get_oid_fieldname(fclass):
    """This retrieves the OID field name from a feature class if it exists.
        Otherwise, None is returned.

    Args:
        fclass (string): A string with the location of the feature class to
        retrieve OID for

    Returns:
        a string containing the OID field name or None
    """
    desc = arcpy.Describe(fclass)
    
    if (desc.hasOID == True):
        return desc.OIDFieldName
    
    return None

def copy_to_new_field(fc, fname, newfname):
    """Adds a new field to the feature clsased named 'newfname' of same
        type as 'fname' and copies the contents.
    """
    
    old_field = arcpy.ListFields(fc, fname)[0]
    
    new_type = translate_ftype_for_addition(old_field.type)
    
    arcpy.AddField_management(fc, newfname, new_type)
    
    rows = arcpy.UpdateCursor(fc)
    
    for row in rows:
        fvalue = row.getValue(fname)
        row.setValue(newfname, fvalue)
        rows.updateRow(row)
    del row, rows

def translate_ftype_for_addition(ftype):
    """Arcpy is stupid and isn't consistent with their type names between 
        describing a field and adding it. This will map them correctly.
    """
    if (ftype == "Integer"):
        return "LONG"
    elif (ftype == "String"):
        return "TEXT"
    elif (ftype == "SmallInteger"):
        return "SHORT"
    elif (ftype == "OID"):
        return "LONG"
    else:
        return ftype
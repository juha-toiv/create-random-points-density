# Copyright (c) 2023 Juha Toivola
# Licensed under the terms of the MIT License
import arcpy

if __name__ == "__main__":
    fc = arcpy.GetParameterAsText(0)
    pnts_per_areal_unit = arcpy.GetParameterAsText(1)
    areal_unit = arcpy.GetParameterAsText(2).split(" ")
    area = int(areal_unit[0])
    unit = areal_unit[1]
    out_fc = arcpy.GetParameterAsText(3)
    m2 = area * arcpy.ArealUnitConversionFactor(unit, "SquareMeters")
    area_field = 'SHAPE@AREA'
    id_field = 'OID@'
    id_field_name = arcpy.Describe(fc).OIDFieldName
    tmp_in_memory_pnt_lyrs = []
    with arcpy.da.SearchCursor(fc, [id_field, area_field]) as cursor:
        for row in cursor:
            row_id = row[0]
            row_area_m2 = row[1]
            selected = arcpy.SelectLayerByAttribute_management(fc, "NEW_SELECTION", id_field_name + " = " + str(row_id))
            number_of_pnts = (int(row_area_m2) / int(m2)) * int(pnts_per_areal_unit)
            tmp_pnt_fc = "tmp_pnt_" + str(row_id)
            tmp_workspace = "memory"
            tmp_in_memory_pnt_lyrs.append(tmp_workspace + "/" + tmp_pnt_fc)
            arcpy.CreateRandomPoints_management(tmp_workspace, tmp_pnt_fc, selected, "", number_of_pnts, "", "POINT")
            arcpy.management.Merge(tmp_in_memory_pnt_lyrs, out_fc)
        # add to map if map active
        try:
            aprx = arcpy.mp.ArcGISProject('CURRENT')
            active_map = aprx.activeMap.name
            aprxMap = aprx.listMaps(active_map)[0]
            aprxMap.addDataFromPath(out_fc)
        except:
            pass
        for in_memory_pnt_lyr in tmp_in_memory_pnt_lyrs:
            arcpy.Delete_management(in_memory_pnt_lyr)

-- Copyright Vector Software Inc.

-- Script Features
TEST.SCRIPT_FEATURE:C_DIRECT_ARRAY_INDEXING
TEST.SCRIPT_FEATURE:CPP_CLASS_OBJECT_REVISION
TEST.SCRIPT_FEATURE:MULTIPLE_UUT_SUPPORT
--
-- Unit: manager
-- Subprogram: Place_Order
TEST.UNIT:manager
TEST.SUBPROGRAM:Place_Order
TEST.NEW
TEST.NAME:(MAP)CSV_Map_Example
TEST.CSV_FILENAME:$(VECTORCAST_DIR)/tutorial/c/csv_test_data.csv
TEST.CSV_DELIMITER:COMMA
TEST.CSV_HEADER_ROWS: 5
TEST.CSV_ROWS_PER_TESTCASE: 1
TEST.CSV_NAME_COL: 1
TEST.CSV_COLUMN_INFO: 2, TEST.VALUE:manager.Place_Order.Table
TEST.CSV_COLUMN_INFO: 3, TEST.VALUE:manager.Place_Order.Seat
TEST.CSV_COLUMN_INFO: 4, TEST.VALUE:manager.Place_Order.Order.Salad
TEST.CSV_COLUMN_INFO: 5, TEST.VALUE:manager.Place_Order.Order.Entree
TEST.CSV_COLUMN_INFO: 6, TEST.VALUE:manager.Place_Order.Order.Beverage
TEST.CSV_COLUMN_INFO: 7, TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Is_Occupied
TEST.CSV_COLUMN_INFO: 8, TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Number_In_Party
TEST.CSV_COLUMN_INFO: 9, TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Order[1].Entree
TEST.CSV_COLUMN_INFO: 10, TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Check_Total
TEST.END
--
--
-- Test Case: PLACE_ORDER.001
--
TEST.UNIT:manager
TEST.SUBPROGRAM:Place_Order
TEST.NEW
TEST.NAME:PLACE_ORDER.001
TEST.VALUE:manager.Place_Order.Table:2
TEST.VALUE:manager.Place_Order.Seat:0
TEST.VALUE:manager.Place_Order.Order.Soup:ONION
TEST.VALUE:manager.Place_Order.Order.Salad:CAESAR
TEST.VALUE:manager.Place_Order.Order.Entree:STEAK
TEST.VALUE:manager.Place_Order.Order.Beverage:MIXED_DRINK
TEST.VALUE:uut_prototype_stubs.Get_Table_Record.return.Number_In_Party:0
TEST.VALUE:uut_prototype_stubs.Get_Table_Record.return.Check_Total:0.0
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Is_Occupied:v_true
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Number_In_Party:1
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Order[0].Dessert:PIE
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Check_Total:12.0..16.0
TEST.NOTES:

This test is the the same test case that should be created
by following all of the steps in the first part of the 
"C Tutorials -> Basic Tutorial" from the VectorCAST 
Getting Started manual.

It shows the basic concepts associated with setting input and
expected values for both the Unit Under Test and Stub Functions.

TEST.END_NOTES:
TEST.END

-- Test Case: PLACE_ORDER.002
TEST.UNIT:manager
TEST.SUBPROGRAM:Place_Order
TEST.NEW
TEST.NAME:PLACE_ORDER.002
TEST.STUB:manager.Add_Included_Dessert
TEST.VALUE:manager.Add_Included_Dessert.Order[0].Dessert:CAKE
TEST.VALUE:manager.Place_Order.Table:2
TEST.VALUE:manager.Place_Order.Seat:0
TEST.VALUE:manager.Place_Order.Order.Soup:ONION
TEST.VALUE:manager.Place_Order.Order.Salad:CAESAR
TEST.VALUE:manager.Place_Order.Order.Entree:STEAK
TEST.VALUE:manager.Place_Order.Order.Beverage:MIXED_DRINK
TEST.VALUE:uut_prototype_stubs.Get_Table_Record.return.Number_In_Party:0
TEST.VALUE:uut_prototype_stubs.Get_Table_Record.return.Check_Total:0.0
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Is_Occupied:v_true
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Number_In_Party:1
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Order[0].Dessert:CAKE
TEST.EXPECTED:uut_prototype_stubs.Update_Table_Record.Data.Check_Total:12.0..16.0
TEST.NOTES:

This test is the the same test case that should be created
by following all of the steps in the second part of the 
"C Tutorials -> Basic Tutorial" from the VectorCAST 
Getting Started manual.

It is similar to the first test, but it uses a stub for the internal
to manager.c function: Add_Included_Dessert.

TEST.END_NOTES:
TEST.END

-- Copyright Vector Software Inc.
--
-- Script Features
TEST.SCRIPT_FEATURE:C_DIRECT_ARRAY_INDEXING
TEST.SCRIPT_FEATURE:CPP_CLASS_OBJECT_REVISION
TEST.SCRIPT_FEATURE:MULTIPLE_UUT_SUPPORT
TEST.SCRIPT_FEATURE:STANDARD_SPACING_R2
TEST.SCRIPT_FEATURE:OVERLOADED_CONST_SUPPORT
--

-- Test Case: (CL)MANAGER::PLACEORDER.001
TEST.UNIT:manager
TEST.SUBPROGRAM:(cl)Manager::PlaceOrder
TEST.NEW
TEST.NAME:(CL)MANAGER::PLACEORDER.001
TEST.VALUE:manager.<<GLOBAL>>.(cl).Manager.Manager.<<constructor>>.Manager().<<call>>:0
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Table:2
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Seat:0
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Soup:Onion
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Salad:Caesar
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Entree:Steak
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Beverage:MixedDrink
TEST.VALUE:uut_prototype_stubs.DataBase::GetTableRecord.Data[0].NumberInParty:0
TEST.VALUE:uut_prototype_stubs.DataBase::GetTableRecord.Data[0].CheckTotal:0
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].IsOccupied:true
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].NumberInParty:1
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].Order[0].Dessert:Pies
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].CheckTotal:12..16
TEST.NOTES:

This test is the the same test case that should be created
by following all of the steps in the first part of the 
"C Tutorials -> Basic Tutorial" from the VectorCAST 
Getting Started manual.

It shows the basic concepts associated with setting input and
expected values for both the Unit Under Test and Stub Functions.

TEST.END_NOTES:
TEST.END

-- Test Case: (CL)MANAGER::PLACEORDER.002
TEST.UNIT:manager
TEST.SUBPROGRAM:(cl)Manager::PlaceOrder
TEST.NEW
TEST.NAME:(CL)MANAGER::PLACEORDER.002
TEST.STUB:manager.(cl)Manager::AddIncludedDessert
TEST.VALUE:manager.<<GLOBAL>>.(cl).Manager.Manager.<<constructor>>.Manager().<<call>>:0
TEST.VALUE:manager.(cl)Manager::AddIncludedDessert.Order[0].Dessert:Cake
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Table:2
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Seat:0
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Soup:Onion
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Salad:Caesar
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Entree:Steak
TEST.VALUE:manager.(cl)Manager::PlaceOrder.Order.Beverage:MixedDrink
TEST.VALUE:uut_prototype_stubs.DataBase::GetTableRecord.Data[0].NumberInParty:0
TEST.VALUE:uut_prototype_stubs.DataBase::GetTableRecord.Data[0].CheckTotal:0
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].IsOccupied:true
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].NumberInParty:1
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].Order[0].Dessert:Cake
TEST.EXPECTED:uut_prototype_stubs.DataBase::UpdateTableRecord.Data[0].CheckTotal:12..16
TEST.NOTES:

This test is the the same test case that should be created
by following all of the steps in the second part of the 
"C Tutorials -> Basic Tutorial" from the VectorCAST 
Getting Started manual.

It is similar to the first test, but it uses a stub for the internal
to manager.c function: Add_Included_Dessert.

TEST.END_NOTES:
TEST.END

import clr

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
import System
from System.Collections.Generic import *
from System.Collections.Generic import List

doc=DocumentManager.Instance.CurrentDBDocument
app=DocumentManager.Instance.CurrentUIApplication.Application
#============================== !! ===============================================================

desniveis=[]
numberColors=[]

Floors = FilteredElementCollector(doc,doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Floors).ToElements()
desniveisFloors=[]
for elem in Floors:
	if(elem.GetParameters("Height Offset From Level")[0].AsDouble()*30.48 != 0):
		desniveis.append((elem.GetParameters("Height Offset From Level")[0].AsDouble()*30.48,"LAJE",elem.GetTypeId() ))
	desniveisFloors.append(elem.GetParameters("Height Offset From Level")[0].AsDouble()*30.48)
	
Beams = FilteredElementCollector(doc,doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_StructuralFraming).ToElements()
desniveisBeams=[]
for elem in Beams:
	if(elem.GetParameters("z Offset Value")[0].AsDouble()*30.48!=0):
		desniveis.append((elem.GetParameters("z Offset Value")[0].AsDouble()*30.48,"VIGA",elem.GetTypeId()))
	desniveisBeams.append(elem.GetParameters("z Offset Value")[0].AsDouble()*30.48)

try:
	numberColors= desniveisFloors + desniveisBeams
	numberColors = list(dict.fromkeys(numberColors))
	numberColors.remove(0)
except:
	numberColors = list(dict.fromkeys(numberColors))

Colors=(Color(255,128,128),Color(128,255,255),Color(128,128,128),Color(0,255,0),Color(255,255,0))


pattern = UnwrapElement(IN[1])  #recebe fillpaterns sólido

def InsertFilter(view, Filter, color):
 view.AddFilter(Filter.Id)
 overrides = OverrideGraphicSettings()
 overrides.SetCutForegroundPatternColor(color).SetCutForegroundPatternId(pattern.Id).SetSurfaceForegroundPatternColor(color).SetSurfaceForegroundPatternId(pattern.Id)
 view.SetFilterOverrides(Filter.Id, overrides)
 
 
def CreateFilter(valueDesnivel, category ):
  
  if(category == "VIGA"):
  	TransactionManager.Instance.EnsureInTransaction(doc)
  	parameter=ParameterValueProvider(ElementId(BuiltInParameter.Z_OFFSET_VALUE))
  	rule=FilterDoubleRule(parameter,FilterNumericEquals(),valueDesnivel/30.48,0)
	tipo=List[ElementId]()
	tipo.Add(ElementId(BuiltInCategory.OST_StructuralFraming))
  	filter=ParameterFilterElement.Create(doc,category+" "+str(float(valueDesnivel)),tipo ,ElementParameterFilter(rule))
  	TransactionManager.Instance.TransactionTaskDone()
  elif(category == "LAJE"):
  	TransactionManager.Instance.EnsureInTransaction(doc)
  	parameter=ParameterValueProvider(ElementId(BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM))
  	rule=FilterDoubleRule(parameter,FilterNumericEquals(),valueDesnivel/30.48,0)
	tipo=List[ElementId]()
	tipo.Add(ElementId(BuiltInCategory.OST_Floors))
  	filter=ParameterFilterElement.Create(doc,category+" "+str(float(valueDesnivel)),tipo ,ElementParameterFilter(rule))
  	TransactionManager.Instance.TransactionTaskDone()
  return filter


for elem in desniveis:
 x=CreateFilter(elem[0],elem[1])
 color=Colors[numberColors.index(elem[0])]
 InsertFilter(doc.ActiveView, x, color)


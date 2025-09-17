import tools
from datetime import datetime
from typing import TypedDict

# OBS: Note that the '_comp' suffix is to indicate an composed strings splitted by "%"

class Zero:
  
  def __init__(self, name:  str, open_date: str, shelved_date:  str, last_change:  str) -> None:
    self.name = name
    self.open_date = datetime.strptime(open_date, tools.iso_datetime)
    self.shelved_date = None if shelved_date == "" else datetime.strptime(open_date, tools.iso_datetime)
    self.last_change = datetime.strptime(last_change, tools.iso_datetime)

  def tsv_string(self) -> str:
    tag = "ZERO"
    array = [tag, self.name, datetime.strftime(self.open_date, tools.iso_datetime), "" if self.shelved_date is None else datetime.strftime(self.shelved_date, tools.iso_datetime), datetime.strftime(self.last_change, tools.iso_datetime)]
    return "\t".join(array)
  
class Entity:

  def __init__(self, id_comp: str, type: str, name_comp: str, country_comp: str, state_comp: str, city_comp:  str, born: str, death: str) -> None:
    self.id = self._parse_composed(id_comp, False)
    self.type = bool(type) #  False for Individual, True for Legal Entity
    self.name = self._parse_composed(name_comp)
    self.country = self._parse_composed(country_comp)
    self.state = self._parse_composed(state_comp)
    self.city = self._parse_composed(city_comp)
    self.born_date = datetime.strptime(born, tools.iso_date)
    self.death_date = None if death == "" else datetime.strptime(death, tools.iso_date)
  
  def _parse_composed(self, value: str, simple: bool = True) -> list[str]:
    new_list = tools.split_composed_str(value)
    if len(new_list) != 2:
      if simple:
        raise ValueError(f"Invalid number of items in the genereted list:\n {new_list}, should have 2 items: [name, code]")
      else:
        raise ValueError(f"Invalid number of items in the genereted list:\n {new_list}, should have 2 items: [document_number, document_type]")
    else:
      return new_list
  
  def tsv_string(self) -> str:
    tag = "ENTI"
    array = [
      tag,
      tools.join_composed_str(self.id),
      "1" if self.type is True else "",
      tools.join_composed_str(self.name),
      tools.join_composed_str(self.country),
      tools.join_composed_str(self.state),
      tools.join_composed_str(self.city),
      datetime.strftime(self.born_date, tools.iso_date),
      "" if self.death_date is None else datetime.strftime(self.death_date, tools.iso_date)
    ]
    return "\t".join(array)

class Account:
  def __init__(self, id: str, name: str, rec_date: str) -> None:
    self.id = id
    self.hierarchy = id.count(".") + 1
    self.name = name
    self.type = "S" if name == name.upper() else "A"
    self.date = datetime.strptime(rec_date, tools.iso_date)
    self.sons_IDs: list[str] = []
    self.balances = {
      "main": {
        "open": 0.0,
        "debits": 0.0,
        "credits": 0.0,
        "close": 0.0
      }
    }

  def parse_ID_and_Name(self) -> None:
    if len(self.id) > 11:
      raise ValueError(f"{self.id} invalid as ID code, lenght higher than 11.")
    if len(self.name) > 37:
      raise ValueError(f"{self.name} invalid as account name, lenght higher than 37.")

  def parent_ID(self) -> str:
    if self.hierarchy == 1:
      return ""
    else:
      array = self.id.split(".")
      return ".".join(array[:(len(array)-1)])
  
  def tsv_string(self) -> str:
    array = ["ACCO", self.id, self.name, datetime.strftime(self.date, tools.iso_date)]
    return "\t".join(array)

class Cost_center:
  def __init__(self, id: str, name: str, open_date: str, close_date: str) -> None:
    self.id = id
    self.name = name
    self.open_date = datetime.strptime(open_date, tools.iso_date)
    self.close_date = None if close_date == "" else datetime.strptime(close_date, tools.iso_date)

  def tsv_string(self) -> str:
    array = ["CCEN", self.id, self.name, datetime.strftime(self.open_date, tools.iso_date), "" if self.close_date is None else datetime.strftime(self.close_date, tools.iso_date)]
    return "\t".join(array)

class Entry:
  def __init__(self, id: str,  entity: str, type: str, rec_date: str, value: str, dr_acc: str, cr_acc: str, history: str, document: str="", dr_ccen: str="", cr_ccen: str="") -> None:
    self.id = id
    self.entity = entity
    self.type = type
    self.date = datetime.strptime(rec_date, tools.iso_date)
    self.value = float(value)
    self.dr_acc = dr_acc
    self.cr_acc = cr_acc
    self.history = history
    self.document = document
    self.dr_ccen = dr_ccen
    self.cr_ccen = cr_ccen

  def _parse_type(self) -> None:
    if self.type not in ["N", "C"]:
      raise ValueError(f"{self.type} invalid as an Entry type. It should be 'N' or 'C'.")
    
  def tsv_string(self) -> str:
    array = ["ENTR" ,self.id, self.entity, self.type, datetime.strftime(self.date, tools.iso_date),  str(self.value), self.dr_acc, self.cr_acc, self.history, self.document,  self.dr_ccen, self.cr_ccen]
    return "\t".join(array)

class File_structure(TypedDict):
  zero: Zero
  entities: dict[str, Entity]
  accounts: dict[str, Account]
  cost_centers: dict[str, Cost_center]
  entries: dict[str, Entry]

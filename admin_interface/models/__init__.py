from enum import Enum


class TypeAnimalChoice(Enum):
    LAPIN = "Lapin"
    CHINCHILLA = "Chinchilla"
    COCHON_DINDE = "Cochon d'inde"


class TypeSupplementChoice(Enum):
    MEDICAMENT = "Médicament par voie orale/inhalation"
    INJECTION = "Médicament par injection"
    VACCINATION = "Mise à jour d'une vaccination"
    HORAIRE = "Majoration horaire"
    SAMEDI = "Majoration récupération le samedi"
    CAGE = "Supplément cage non fournie"


class SexeChoice(Enum):
    F = "Féminin"
    M = "Masculin"


class EmplacementChoice(Enum):
    PENSION = "Pension"
    REFUGE = "Refuge"


class OrigineChoice(Enum):
    ABANDON = "Abandon particulier"
    REFUGE = "Transfert refuge"
    FOURRIERE = "Fourrière"
    AUTRE = "Autre"


class OuiNonChoice(Enum):
    OUI = "Oui"
    NON = "Non"


class TypeVisiteVetoChoice(Enum):
    VAC = "Vaccination"
    STE = "Stérilisation"
    CHECK = "Checkup"
    AUTRE = "Autre"

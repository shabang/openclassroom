from enum import Enum


class TypeAnimalChoice(Enum):
    LAPIN = "Lapin"
    CHINCHILLA = "Chinchilla"
    COCHON_DINDE = "Cochon d'inde"
    HAMSTER = "Cochon d'inde"
    CHAT = "Chat"


class TypeSupplementChoice(Enum):
    MEDICAMENT = "Médicament par voie orale/inhalation"
    INJECTION = "Médicament par injection"
    VACCINATION = "Mise à jour d'une vaccination"
    HORAIRE = "Majoration horaire"
    SAMEDI = "Majoration récupération le samedi"
    CAGE = "Supplément cage non fournie"
    COHABITATION_LIBRE = "Cohabitation Libre"
    COHABITATION_FORCEE = "Cohabitation Forcée"


class SexeChoice(Enum):
    F = "Féminin"
    M = "Masculin"
    NI = "Non identifié"


class EmplacementChoice(Enum):
    PENSION = "Pension"
    REFUGE = "Refuge"


class OrigineChoice(Enum):
    ABANDON = "Abandon particulier"
    REFUGE = "Transfert refuge"
    FOURRIERE = "Fourrière"
    LABO = "Laboratoire"
    AUTRE = "Autre"


class OuiNonChoice(Enum):
    OUI = "Oui"
    NON = "Non"


class TypeVisiteVetoChoice(Enum):
    VAC = "Vaccination"
    STE = "Stérilisation"
    CHECK = "Checkup"
    AUTRE = "Autre"

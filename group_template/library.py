"""Curated library of substituent group templates.

Every entry's SMILES starts with a ``*`` dummy, so **atom index 0 is the
attachment point** and atom 1 is the group's first real atom. RDKit preserves
input atom order, so the dummy written first is index 0.

The dummy stands in for the atom you click: the group is bonded to that atom,
which keeps its own element (see ``placement.py``).
"""

from typing import List, NamedTuple


class Group(NamedTuple):
    """One abbreviation entry in the palette."""

    label: str
    smiles: str
    category: str
    aliases: str = ""


ALKYL = "Alkyl"
CYCLOALKYL = "Cycloalkyl"
HALOALKYL = "Halogenated"
UNSATURATED = "Alkenyl / Alkynyl"
ARYL = "Aryl"
HETEROARYL = "Heteroaryl"
SATURATED_HETERO = "Saturated heterocycle"
ACYL = "Acyl / Ester / Amide"
PG_O = "Protecting group (O)"
PG_N = "Protecting group (N)"
SILYL = "Silyl"
SULFUR = "Sulfonyl / S"
PHOSPHORUS = "Phosphorus"
METALLOID = "B / Sn / Metal"
FUNCTIONAL = "Functional group"
SIDECHAIN = "Amino acid side chain"
NUCLEOBASE = "Nucleobase"

GROUPS: List[Group] = [
    # --- Alkyl ---
    Group("Me", "*C", ALKYL, "methyl"),
    Group("Et", "*CC", ALKYL, "ethyl"),
    Group("nPr", "*CCC", ALKYL, "n-propyl"),
    Group("iPr", "*C(C)C", ALKYL, "isopropyl 2-propyl"),
    Group("nBu", "*CCCC", ALKYL, "n-butyl"),
    Group("iBu", "*CC(C)C", ALKYL, "isobutyl CH2iPr 2-methylpropyl"),
    Group("sBu", "*C(C)CC", ALKYL, "sec-butyl"),
    Group("tBu", "*C(C)(C)C", ALKYL, "tert-butyl"),
    Group("nPent", "*CCCCC", ALKYL, "n-pentyl amyl"),
    Group("neoPent", "*CC(C)(C)C", ALKYL, "neopentyl CH2tBu 2,2-dimethylpropyl"),
    Group("nHex", "*CCCCCC", ALKYL, "n-hexyl"),
    Group("nHept", "*CCCCCCC", ALKYL, "n-heptyl"),
    Group("nOct", "*CCCCCCCC", ALKYL, "n-octyl"),
    Group("nDec", "*CCCCCCCCCC", ALKYL, "n-decyl"),
    Group("nDodec", "*CCCCCCCCCCCC", ALKYL, "n-dodecyl lauryl"),
    Group("nHexadec", "*CCCCCCCCCCCCCCCC", ALKYL, "n-hexadecyl cetyl palmityl"),
    Group("CHMePh", "*C(C)c1ccccc1", ALKYL, "1-phenylethyl"),
    Group("CHPh2", "*C(c1ccccc1)c1ccccc1", ALKYL, "benzhydryl diphenylmethyl"),
    Group("CPh3", "*C(c1ccccc1)(c1ccccc1)c1ccccc1", ALKYL, "trityl Trt"),
    # --- Cycloalkyl ---
    Group("cPr", "*C1CC1", CYCLOALKYL, "cyclopropyl"),
    Group("cBu", "*C1CCC1", CYCLOALKYL, "cyclobutyl"),
    Group("cPent", "*C1CCCC1", CYCLOALKYL, "cyclopentyl"),
    Group("cHex", "*C1CCCCC1", CYCLOALKYL, "cyclohexyl Cy"),
    Group("cHept", "*C1CCCCCC1", CYCLOALKYL, "cycloheptyl"),
    Group("cOct", "*C1CCCCCCC1", CYCLOALKYL, "cyclooctyl"),
    Group("CH2cPr", "*CC1CC1", CYCLOALKYL, "cyclopropylmethyl"),
    Group("1-Ad", "*C12CC3CC(CC(C3)C1)C2", CYCLOALKYL, "adamantyl adamantan-1-yl"),
    Group("2-Ad", "*C1C2CC3CC1CC(C2)C3", CYCLOALKYL, "adamantan-2-yl"),
    Group(
        "2-Norbornyl",
        "*C1CC2CCC1C2",
        CYCLOALKYL,
        "norbornan-2-yl bicyclo[2.2.1]heptan-2-yl",
    ),
    Group("cHexenyl", "*C1=CCCCC1", CYCLOALKYL, "cyclohex-1-en-1-yl"),
    Group("Bicyclopentyl", "*C12CC(C1)C2", CYCLOALKYL, "bicyclo[1.1.1]pentyl BCP"),
    # --- Halogenated ---
    Group("CH2F", "*CF", HALOALKYL, "fluoromethyl"),
    Group("CHF2", "*C(F)F", HALOALKYL, "difluoromethyl"),
    Group("CF3", "*C(F)(F)F", HALOALKYL, "trifluoromethyl"),
    Group("CH2Cl", "*CCl", HALOALKYL, "chloromethyl"),
    Group("CHCl2", "*C(Cl)Cl", HALOALKYL, "dichloromethyl"),
    Group("CCl3", "*C(Cl)(Cl)Cl", HALOALKYL, "trichloromethyl"),
    Group("CH2Br", "*CBr", HALOALKYL, "bromomethyl"),
    Group("CBr3", "*C(Br)(Br)Br", HALOALKYL, "tribromomethyl"),
    Group("CH2I", "*CI", HALOALKYL, "iodomethyl"),
    Group("C2F5", "*C(F)(F)C(F)(F)F", HALOALKYL, "pentafluoroethyl perfluoroethyl"),
    Group("nC3F7", "*C(F)(F)C(F)(F)C(F)(F)F", HALOALKYL, "heptafluoropropyl"),
    Group("iC3F7", "*C(F)(C(F)(F)F)C(F)(F)F", HALOALKYL, "heptafluoroisopropyl"),
    Group("nC4F9", "*C(F)(F)C(F)(F)C(F)(F)C(F)(F)F", HALOALKYL, "nonafluorobutyl"),
    Group("CH2CF3", "*CC(F)(F)F", HALOALKYL, "2,2,2-trifluoroethyl"),
    Group("CH2CH2Cl", "*CCCl", HALOALKYL, "2-chloroethyl"),
    # --- Alkenyl / Alkynyl ---
    Group("Vinyl", "*C=C", UNSATURATED, "ethenyl"),
    Group("Allyl", "*CC=C", UNSATURATED, "prop-2-en-1-yl"),
    Group("Homoallyl", "*CCC=C", UNSATURATED, "but-3-en-1-yl"),
    Group("1-Propenyl", "*C=CC", UNSATURATED, "propenyl"),
    Group("Isopropenyl", "*C(=C)C", UNSATURATED, "prop-1-en-2-yl"),
    Group("Prenyl", "*CC=C(C)C", UNSATURATED, "3-methylbut-2-enyl dimethylallyl"),
    Group("Methallyl", "*CC(=C)C", UNSATURATED, "2-methylallyl"),
    Group("Styryl", "*C=Cc1ccccc1", UNSATURATED, "2-phenylvinyl beta-styryl"),
    Group("Cinnamyl", "*CC=Cc1ccccc1", UNSATURATED, "3-phenylallyl"),
    Group("1,3-Butadienyl", "*C=CC=C", UNSATURATED, "butadienyl"),
    Group("Ethynyl", "*C#C", UNSATURATED, "acetylenyl"),
    Group("Propargyl", "*CC#C", UNSATURATED, "prop-2-yn-1-yl"),
    Group("1-Propynyl", "*C#CC", UNSATURATED, "methylacetylenyl"),
    Group("TMS-ethynyl", "*C#C[Si](C)(C)C", UNSATURATED, "trimethylsilylacetylenyl"),
    Group("Phenylethynyl", "*C#Cc1ccccc1", UNSATURATED, "alkynylbenzene"),
    Group("Allenyl", "*C=C=C", UNSATURATED, "propadienyl"),
    # --- Aryl ---
    Group("Ph", "*c1ccccc1", ARYL, "phenyl benzene"),
    Group("Bn", "*Cc1ccccc1", ARYL, "benzyl"),
    Group("Phenethyl", "*CCc1ccccc1", ARYL, "2-phenylethyl"),
    Group("o-Tol", "*c1ccccc1C", ARYL, "2-methylphenyl ortho-tolyl"),
    Group("m-Tol", "*c1cccc(C)c1", ARYL, "3-methylphenyl meta-tolyl"),
    Group("p-Tol", "*c1ccc(C)cc1", ARYL, "4-methylphenyl para-tolyl"),
    Group("Xyl", "*c1c(C)cccc1C", ARYL, "2,6-dimethylphenyl 2,6-xylyl"),
    Group("Mes", "*c1c(C)cc(C)cc1C", ARYL, "mesityl 2,4,6-trimethylphenyl"),
    Group("Dipp", "*c1c(C(C)C)cccc1C(C)C", ARYL, "2,6-diisopropylphenyl"),
    Group(
        "Tripp",
        "*c1c(C(C)C)cc(C(C)C)cc1C(C)C",
        ARYL,
        "2,4,6-triisopropylphenyl Tip",
    ),
    Group("Dur", "*c1c(C)c(C)cc(C)c1C", ARYL, "duryl 2,3,5,6-tetramethylphenyl"),
    Group("PMP", "*c1ccc(OC)cc1", ARYL, "4-methoxyphenyl methoxybenzene"),
    Group("4-ClC6H4", "*c1ccc(Cl)cc1", ARYL, "4-chlorophenyl"),
    Group("4-BrC6H4", "*c1ccc(Br)cc1", ARYL, "4-bromophenyl"),
    Group("4-FC6H4", "*c1ccc(F)cc1", ARYL, "4-fluorophenyl"),
    Group("4-CF3C6H4", "*c1ccc(C(F)(F)F)cc1", ARYL, "4-(trifluoromethyl)phenyl"),
    Group("4-NO2C6H4", "*c1ccc([N+](=O)[O-])cc1", ARYL, "4-nitrophenyl PNP"),
    Group("4-CNC6H4", "*c1ccc(C#N)cc1", ARYL, "4-cyanophenyl"),
    Group("4-tBuC6H4", "*c1ccc(C(C)(C)C)cc1", ARYL, "4-tert-butylphenyl"),
    Group("4-HOC6H4", "*c1ccc(O)cc1", ARYL, "4-hydroxyphenyl"),
    Group("4-Me2NC6H4", "*c1ccc(N(C)C)cc1", ARYL, "4-(dimethylamino)phenyl"),
    Group("2-Pyridylphenyl", "*c1ccccc1-c1ccccn1", ARYL, "2-(pyridin-2-yl)phenyl"),
    Group(
        "3,5-(CF3)2C6H3",
        "*c1cc(C(F)(F)F)cc(C(F)(F)F)c1",
        ARYL,
        "3,5-bis(trifluoromethyl)phenyl ArF",
    ),
    Group("C6F5", "*c1c(F)c(F)c(F)c(F)c1F", ARYL, "pentafluorophenyl Pfp"),
    Group("1-Naph", "*c1cccc2ccccc12", ARYL, "naphthalen-1-yl"),
    Group("2-Naph", "*c1ccc2ccccc2c1", ARYL, "naphthalen-2-yl"),
    Group("9-Anthryl", "*c1c2ccccc2cc2ccccc12", ARYL, "anthracen-9-yl meso"),
    Group("1-Pyrenyl", "*c1ccc2ccc3cccc4ccc1c2c34", ARYL, "pyren-1-yl"),
    Group("Biphenyl-4-yl", "*c1ccc(-c2ccccc2)cc1", ARYL, "4-biphenylyl"),
    Group("Benzhydryl", "*C(c1ccccc1)c1ccccc1", ARYL, "diphenylmethyl"),
    # --- Heteroaryl ---
    Group("2-Py", "*c1ccccn1", HETEROARYL, "pyridin-2-yl"),
    Group("3-Py", "*c1cccnc1", HETEROARYL, "pyridin-3-yl"),
    Group("4-Py", "*c1ccncc1", HETEROARYL, "pyridin-4-yl"),
    Group("2-Furyl", "*c1ccco1", HETEROARYL, "furan-2-yl"),
    Group("3-Furyl", "*c1cocc1", HETEROARYL, "furan-3-yl"),
    Group("2-Thienyl", "*c1cccs1", HETEROARYL, "thiophen-2-yl"),
    Group("3-Thienyl", "*c1cscc1", HETEROARYL, "thiophen-3-yl"),
    Group("N-Pyrrolyl", "*n1cccc1", HETEROARYL, "pyrrol-1-yl"),
    Group("2-Pyrrolyl", "*c1ccc[nH]1", HETEROARYL, "pyrrol-2-yl"),
    Group("N-Imidazolyl", "*n1ccnc1", HETEROARYL, "imidazol-1-yl"),
    Group("2-Imidazolyl", "*c1ncc[nH]1", HETEROARYL, "imidazol-2-yl"),
    Group("N-Pyrazolyl", "*n1cccn1", HETEROARYL, "pyrazol-1-yl"),
    Group("N-Triazolyl", "*n1ccnn1", HETEROARYL, "1,2,3-triazol-1-yl click"),
    Group("5-Tetrazolyl", "*c1nnn[nH]1", HETEROARYL, "tetrazol-5-yl"),
    Group("2-Oxazolyl", "*c1ncco1", HETEROARYL, "oxazol-2-yl"),
    Group("2-Thiazolyl", "*c1nccs1", HETEROARYL, "thiazol-2-yl"),
    Group("2-Pyrimidyl", "*c1ncccn1", HETEROARYL, "pyrimidin-2-yl"),
    Group("2-Pyrazinyl", "*c1cnccn1", HETEROARYL, "pyrazin-2-yl"),
    Group("3-Pyridazinyl", "*c1cccnn1", HETEROARYL, "pyridazin-3-yl"),
    Group("2-Quinolyl", "*c1ccc2ccccc2n1", HETEROARYL, "quinolin-2-yl"),
    Group("8-Quinolyl", "*c1cccc2cccnc12", HETEROARYL, "quinolin-8-yl"),
    Group("3-Indolyl", "*c1c[nH]c2ccccc12", HETEROARYL, "indol-3-yl"),
    Group("N-Indolyl", "*n1ccc2ccccc12", HETEROARYL, "indol-1-yl"),
    Group("2-Benzofuryl", "*c1cc2ccccc2o1", HETEROARYL, "benzofuran-2-yl"),
    Group("2-Benzothienyl", "*c1cc2ccccc2s1", HETEROARYL, "benzothiophen-2-yl"),
    Group("2-Benzimidazolyl", "*c1nc2ccccc2[nH]1", HETEROARYL, "benzimidazol-2-yl"),
    Group("2-Benzothiazolyl", "*c1nc2ccccc2s1", HETEROARYL, "benzothiazol-2-yl"),
    Group("N-Carbazolyl", "*n1c2ccccc2c2ccccc21", HETEROARYL, "carbazol-9-yl"),
    Group("2-Furfuryl", "*Cc1ccco1", HETEROARYL, "furfuryl furan-2-ylmethyl"),
    Group("Picolyl", "*Cc1ccccn1", HETEROARYL, "pyridin-2-ylmethyl"),
    # --- Saturated heterocycles ---
    Group("N-Piperidyl", "*N1CCCCC1", SATURATED_HETERO, "piperidin-1-yl"),
    Group("N-Pyrrolidinyl", "*N1CCCC1", SATURATED_HETERO, "pyrrolidin-1-yl"),
    Group("N-Morpholino", "*N1CCOCC1", SATURATED_HETERO, "morpholin-4-yl"),
    Group("N-Piperazinyl", "*N1CCNCC1", SATURATED_HETERO, "piperazin-1-yl"),
    Group(
        "N-Me-piperazinyl", "*N1CCN(C)CC1", SATURATED_HETERO, "4-methylpiperazin-1-yl"
    ),
    Group("N-Azetidinyl", "*N1CCC1", SATURATED_HETERO, "azetidin-1-yl"),
    Group("N-Aziridinyl", "*N1CC1", SATURATED_HETERO, "aziridin-1-yl"),
    Group("4-Piperidyl", "*C1CCNCC1", SATURATED_HETERO, "piperidin-4-yl"),
    Group("3-Pyrrolidinyl", "*C1CCNC1", SATURATED_HETERO, "pyrrolidin-3-yl"),
    Group("2-THF", "*C1CCCO1", SATURATED_HETERO, "tetrahydrofuran-2-yl"),
    Group("2-THP", "*C1CCCCO1", SATURATED_HETERO, "tetrahydropyran-2-yl"),
    Group("4-THP", "*C1CCOCC1", SATURATED_HETERO, "tetrahydropyran-4-yl oxan-4-yl"),
    Group("3-Oxetanyl", "*C1COC1", SATURATED_HETERO, "oxetan-3-yl"),
    Group("Oxiranyl", "*C1CO1", SATURATED_HETERO, "epoxide oxiran-2-yl"),
    Group("Dioxolan-2-yl", "*C1OCCO1", SATURATED_HETERO, "protected aldehyde acetal"),
    Group("1,3-Dioxan-2-yl", "*C1OCCCO1", SATURATED_HETERO, "1,3-dioxan-2-yl acetal"),
    Group(
        "1,3-Dithian-2-yl", "*C1SCCCS1", SATURATED_HETERO, "1,3-dithian-2-yl umpolung"
    ),
    Group("N-Succinimidyl", "*N1C(=O)CCC1=O", SATURATED_HETERO, "succinimide NHS"),
    Group("Phth", "*N1C(=O)c2ccccc2C1=O", SATURATED_HETERO, "phthalimido phthalimide"),
    # --- Acyl / Ester / Amide ---
    Group("CHO", "*C=O", ACYL, "formyl aldehyde"),
    Group("Ac", "*C(C)=O", ACYL, "acetyl"),
    Group("Propionyl", "*C(=O)CC", ACYL, "EtCO propanoyl"),
    Group("Piv", "*C(=O)C(C)(C)C", ACYL, "pivaloyl trimethylacetyl"),
    Group("Bz", "*C(=O)c1ccccc1", ACYL, "benzoyl"),
    Group("4-NO2-Bz", "*C(=O)c1ccc([N+](=O)[O-])cc1", ACYL, "4-nitrobenzoyl"),
    Group("TFA", "*C(=O)C(F)(F)F", ACYL, "trifluoroacetyl"),
    Group("COOH", "*C(=O)O", ACYL, "carboxyl carboxylic acid"),
    Group("CO2Me", "*C(=O)OC", ACYL, "methyl ester methoxycarbonyl"),
    Group("CO2Et", "*C(=O)OCC", ACYL, "ethyl ester ethoxycarbonyl"),
    Group("CO2tBu", "*C(=O)OC(C)(C)C", ACYL, "tert-butyl ester"),
    Group("CO2Bn", "*C(=O)OCc1ccccc1", ACYL, "benzyl ester"),
    Group("CO2Ph", "*C(=O)Oc1ccccc1", ACYL, "phenyl ester"),
    Group("CONH2", "*C(N)=O", ACYL, "primary amide carbamoyl"),
    Group("CONHMe", "*C(=O)NC", ACYL, "N-methylamide"),
    Group("CONMe2", "*C(=O)N(C)C", ACYL, "N,N-dimethylamide"),
    Group("CONHPh", "*C(=O)Nc1ccccc1", ACYL, "anilide"),
    Group("Weinreb", "*C(=O)N(C)OC", ACYL, "N-methoxy-N-methylamide"),
    Group("COCl", "*C(Cl)=O", ACYL, "acyl chloride chlorocarbonyl"),
    Group("COF", "*C(F)=O", ACYL, "acyl fluoride"),
    Group("CSNH2", "*C(N)=S", ACYL, "thioamide"),
    Group("Xanthate", "*C(=S)SC", ACYL, "S-methyl dithiocarbonate"),
    Group("COSMe", "*C(=O)SC", ACYL, "thioester"),
    Group("Oxalyl-OMe", "*C(=O)C(=O)OC", ACYL, "methyl oxalyl"),
    # --- Protecting groups (O) ---
    Group("MOM", "*COC", PG_O, "methoxymethyl"),
    Group("MEM", "*COCCOC", PG_O, "methoxyethoxymethyl"),
    Group("BOM", "*COCc1ccccc1", PG_O, "benzyloxymethyl"),
    Group("SEM", "*COCC[Si](C)(C)C", PG_O, "trimethylsilylethoxymethyl"),
    Group("THP-O", "*C1CCCCO1", PG_O, "tetrahydropyranyl"),
    Group("PMB", "*Cc1ccc(OC)cc1", PG_O, "para-methoxybenzyl MPM"),
    Group("Trt", "*C(c1ccccc1)(c1ccccc1)c1ccccc1", PG_O, "trityl triphenylmethyl"),
    Group(
        "DMTr",
        "*C(c1ccc(OC)cc1)(c1ccc(OC)cc1)c1ccccc1",
        PG_O,
        "4,4'-dimethoxytrityl nucleoside",
    ),
    Group(
        "MMTr",
        "*C(c1ccc(OC)cc1)(c1ccccc1)c1ccccc1",
        PG_O,
        "4-methoxytrityl monomethoxytrityl",
    ),
    Group("Piv-O", "*C(=O)C(C)(C)C", PG_O, "pivaloate"),
    Group("Ac-O", "*C(C)=O", PG_O, "acetate"),
    Group("Bz-O", "*C(=O)c1ccccc1", PG_O, "benzoate"),
    Group("Allyl-O", "*CC=C", PG_O, "allyl ether"),
    Group("Bn-O", "*Cc1ccccc1", PG_O, "benzyl ether"),
    # --- Protecting groups (N) ---
    Group("Boc", "*C(=O)OC(C)(C)C", PG_N, "tert-butoxycarbonyl"),
    Group("Cbz", "*C(=O)OCc1ccccc1", PG_N, "benzyloxycarbonyl Z"),
    Group(
        "Fmoc",
        "*C(=O)OCC1c2ccccc2-c2ccccc21",
        PG_N,
        "fluorenylmethyloxycarbonyl peptide",
    ),
    Group("Alloc", "*C(=O)OCC=C", PG_N, "allyloxycarbonyl"),
    Group("Troc", "*C(=O)OCC(Cl)(Cl)Cl", PG_N, "trichloroethoxycarbonyl"),
    Group("Teoc", "*C(=O)OCC[Si](C)(C)C", PG_N, "trimethylsilylethoxycarbonyl"),
    Group("Moc", "*C(=O)OC", PG_N, "methoxycarbonyl carbamate"),
    Group("Adoc", "*C(=O)OC12CC3CC(CC(C3)C1)C2", PG_N, "adamantyloxycarbonyl"),
    Group("Bn-N", "*Cc1ccccc1", PG_N, "N-benzyl"),
    Group("DMB", "*Cc1ccc(OC)cc1OC", PG_N, "2,4-dimethoxybenzyl"),
    Group("Trt-N", "*C(c1ccccc1)(c1ccccc1)c1ccccc1", PG_N, "N-trityl"),
    Group("Bus", "*S(=O)(=O)C(C)(C)C", PG_N, "tert-butylsulfonyl"),
    Group(
        "tBu-sulfinyl", "*S(=O)C(C)(C)C", PG_N, "tert-butanesulfinyl Ellman sulfinamide"
    ),
    # --- Silyl ---
    Group("TMS", "*[Si](C)(C)C", SILYL, "trimethylsilyl"),
    Group("TES", "*[Si](CC)(CC)CC", SILYL, "triethylsilyl"),
    Group("TIPS", "*[Si](C(C)C)(C(C)C)C(C)C", SILYL, "triisopropylsilyl"),
    Group("TBS", "*[Si](C)(C)C(C)(C)C", SILYL, "TBDMS tert-butyldimethylsilyl"),
    Group(
        "TBDPS",
        "*[Si](c1ccccc1)(c1ccccc1)C(C)(C)C",
        SILYL,
        "tert-butyldiphenylsilyl",
    ),
    Group("TPS", "*[Si](c1ccccc1)(c1ccccc1)c1ccccc1", SILYL, "triphenylsilyl"),
    Group("DMPS", "*[Si](C)(C)c1ccccc1", SILYL, "dimethylphenylsilyl"),
    Group("TMSE", "*CC[Si](C)(C)C", SILYL, "2-(trimethylsilyl)ethyl"),
    Group("SiMe2H", "*[SiH](C)C", SILYL, "dimethylsilyl"),
    # --- Sulfonyl / S ---
    Group("Ms", "*S(C)(=O)=O", SULFUR, "mesyl methanesulfonyl"),
    Group("Ts", "*S(=O)(=O)c1ccc(C)cc1", SULFUR, "tosyl para-toluenesulfonyl"),
    Group("Tf", "*S(=O)(=O)C(F)(F)F", SULFUR, "triflyl trifluoromethanesulfonyl"),
    Group(
        "Bs", "*S(=O)(=O)c1ccccc1", SULFUR, "besyl benzenesulfonyl SO2Ph phenylsulfonyl"
    ),
    Group(
        "4-Ns",
        "*S(=O)(=O)c1ccc([N+](=O)[O-])cc1",
        SULFUR,
        "nosyl 4-nitrobenzenesulfonyl",
    ),
    Group(
        "2-Ns",
        "*S(=O)(=O)c1ccccc1[N+](=O)[O-]",
        SULFUR,
        "2-nitrobenzenesulfonyl Fukuyama",
    ),
    Group("SO3H", "*S(=O)(=O)O", SULFUR, "sulfo sulfonic acid"),
    Group("SO2NH2", "*S(N)(=O)=O", SULFUR, "sulfamoyl sulfonamide"),
    Group("SO2Cl", "*S(Cl)(=O)=O", SULFUR, "sulfonyl chloride"),
    Group("SH", "*S", SULFUR, "thiol mercapto"),
    Group("SMe", "*SC", SULFUR, "methylthio"),
    Group("SEt", "*SCC", SULFUR, "ethylthio"),
    Group("StBu", "*SC(C)(C)C", SULFUR, "tert-butylthio"),
    Group("SPh", "*Sc1ccccc1", SULFUR, "phenylthio phenylsulfanyl"),
    Group("SBn", "*SCc1ccccc1", SULFUR, "benzylthio"),
    Group("SAc", "*SC(C)=O", SULFUR, "thioacetate"),
    Group("SCF3", "*SC(F)(F)F", SULFUR, "trifluoromethylthio"),
    Group("SCN", "*SC#N", SULFUR, "thiocyanato"),
    Group("SOMe", "*S(C)=O", SULFUR, "methylsulfinyl"),
    # --- Phosphorus ---
    Group("PPh2", "*P(c1ccccc1)c1ccccc1", PHOSPHORUS, "diphenylphosphino"),
    Group("PMe2", "*P(C)C", PHOSPHORUS, "dimethylphosphino"),
    Group("PCy2", "*P(C1CCCCC1)C1CCCCC1", PHOSPHORUS, "dicyclohexylphosphino"),
    Group("PtBu2", "*P(C(C)(C)C)C(C)(C)C", PHOSPHORUS, "di-tert-butylphosphino"),
    Group("POPh2", "*P(=O)(c1ccccc1)c1ccccc1", PHOSPHORUS, "diphenylphosphoryl"),
    Group("PO(OEt)2", "*P(=O)(OCC)OCC", PHOSPHORUS, "diethylphosphonate HWE"),
    Group("PO(OMe)2", "*P(=O)(OC)OC", PHOSPHORUS, "dimethylphosphonate"),
    Group("PO3H2", "*P(=O)(O)O", PHOSPHORUS, "phosphono phosphonic acid"),
    Group("OPO(OEt)2", "*OP(=O)(OCC)OCC", PHOSPHORUS, "diethyl phosphate"),
    Group(
        "PPh3+", "*[P+](c1ccccc1)(c1ccccc1)c1ccccc1", PHOSPHORUS, "phosphonium Wittig"
    ),
    # --- B / Sn / Metal ---
    Group("B(OH)2", "*B(O)O", METALLOID, "boronic acid"),
    Group("Bpin", "*B1OC(C)(C)C(C)(C)O1", METALLOID, "pinacol boronate"),
    Group("Bneop", "*B1OCC(C)(C)CO1", METALLOID, "neopentyl glycol boronate"),
    Group("BF3-", "*[B-](F)(F)F", METALLOID, "trifluoroborate"),
    Group("BEt2", "*B(CC)CC", METALLOID, "diethylboryl"),
    Group("SnBu3", "*[Sn](CCCC)(CCCC)CCCC", METALLOID, "tributylstannyl Stille"),
    Group("SnMe3", "*[Sn](C)(C)C", METALLOID, "trimethylstannyl"),
    Group("MgBr", "*[Mg]Br", METALLOID, "Grignard"),
    Group("ZnBr", "*[Zn]Br", METALLOID, "organozinc Negishi"),
    Group("Li", "*[Li]", METALLOID, "organolithium"),
    Group("HgCl", "*[Hg]Cl", METALLOID, "chloromercurio"),
    # --- Simple functional groups ---
    Group("OH", "*O", FUNCTIONAL, "hydroxy alcohol"),
    Group("OMe", "*OC", FUNCTIONAL, "methoxy"),
    Group("OEt", "*OCC", FUNCTIONAL, "ethoxy"),
    Group("OiPr", "*OC(C)C", FUNCTIONAL, "isopropoxy"),
    Group("OtBu", "*OC(C)(C)C", FUNCTIONAL, "tert-butoxy"),
    Group("OPh", "*Oc1ccccc1", FUNCTIONAL, "phenoxy"),
    Group("OBn", "*OCc1ccccc1", FUNCTIONAL, "benzyloxy"),
    Group("OAc", "*OC(C)=O", FUNCTIONAL, "acetoxy acetate"),
    Group("OTs", "*OS(=O)(=O)c1ccc(C)cc1", FUNCTIONAL, "tosylate"),
    Group("OMs", "*OS(C)(=O)=O", FUNCTIONAL, "mesylate"),
    Group("OTf", "*OS(=O)(=O)C(F)(F)F", FUNCTIONAL, "triflate"),
    Group("OTMS", "*O[Si](C)(C)C", FUNCTIONAL, "trimethylsilyloxy"),
    Group("OTBS", "*O[Si](C)(C)C(C)(C)C", FUNCTIONAL, "TBS ether silyloxy"),
    Group("OCF3", "*OC(F)(F)F", FUNCTIONAL, "trifluoromethoxy"),
    Group("OCHF2", "*OC(F)F", FUNCTIONAL, "difluoromethoxy"),
    Group("OCH2CH2OH", "*OCCO", FUNCTIONAL, "hydroxyethoxy"),
    Group(
        "OMe-PEG2",
        "*OCCOCCOC",
        FUNCTIONAL,
        "PEG oligoethylene glycol methoxyethoxyethoxy",
    ),
    Group("NH2", "*N", FUNCTIONAL, "amino amine"),
    Group("NHMe", "*NC", FUNCTIONAL, "methylamino"),
    Group("NMe2", "*N(C)C", FUNCTIONAL, "dimethylamino"),
    Group("NEt2", "*N(CC)CC", FUNCTIONAL, "diethylamino"),
    Group("NHPh", "*Nc1ccccc1", FUNCTIONAL, "anilino phenylamino"),
    Group("NHAc", "*NC(C)=O", FUNCTIONAL, "acetamido"),
    Group("NHBoc", "*NC(=O)OC(C)(C)C", FUNCTIONAL, "Boc-protected amine"),
    Group("NHCbz", "*NC(=O)OCc1ccccc1", FUNCTIONAL, "Cbz-protected amine"),
    Group("NHTs", "*NS(=O)(=O)c1ccc(C)cc1", FUNCTIONAL, "tosylamide"),
    Group("NHNH2", "*NN", FUNCTIONAL, "hydrazino"),
    Group("N3", "*N=[N+]=[N-]", FUNCTIONAL, "azido azide"),
    Group("NO2", "*[N+](=O)[O-]", FUNCTIONAL, "nitro"),
    Group("NO", "*N=O", FUNCTIONAL, "nitroso"),
    Group("N=NPh", "*N=Nc1ccccc1", FUNCTIONAL, "phenylazo diazenyl"),
    Group("NMe3+", "*[N+](C)(C)C", FUNCTIONAL, "trimethylammonium"),
    Group("CN", "*C#N", FUNCTIONAL, "cyano nitrile"),
    Group("NC", "*[N+]#[C-]", FUNCTIONAL, "isocyano isonitrile"),
    Group("NCO", "*N=C=O", FUNCTIONAL, "isocyanato"),
    Group("NCS", "*N=C=S", FUNCTIONAL, "isothiocyanato"),
    Group("OCN", "*OC#N", FUNCTIONAL, "cyanato"),
    Group("F", "*F", FUNCTIONAL, "fluoro"),
    Group("Cl", "*Cl", FUNCTIONAL, "chloro"),
    Group("Br", "*Br", FUNCTIONAL, "bromo"),
    Group("I", "*I", FUNCTIONAL, "iodo"),
    Group("CH2OH", "*CO", FUNCTIONAL, "hydroxymethyl"),
    Group("CH2OMe", "*COC", FUNCTIONAL, "methoxymethyl"),
    Group("CH2NH2", "*CN", FUNCTIONAL, "aminomethyl"),
    Group("CH2CN", "*CC#N", FUNCTIONAL, "cyanomethyl"),
    Group("CH2COOH", "*CC(=O)O", FUNCTIONAL, "carboxymethyl"),
    # --- Amino acid side chains ---
    Group("Ala", "*C", SIDECHAIN, "alanine methyl"),
    Group("Val", "*C(C)C", SIDECHAIN, "valine isopropyl"),
    Group("Leu", "*CC(C)C", SIDECHAIN, "leucine isobutyl"),
    Group("Ile", "*C(C)CC", SIDECHAIN, "isoleucine sec-butyl"),
    Group("Ser", "*CO", SIDECHAIN, "serine hydroxymethyl"),
    Group("Thr", "*C(C)O", SIDECHAIN, "threonine"),
    Group("Cys", "*CS", SIDECHAIN, "cysteine thiomethyl"),
    Group("Met", "*CCSC", SIDECHAIN, "methionine"),
    Group("Asp", "*CC(=O)O", SIDECHAIN, "aspartate carboxymethyl"),
    Group("Glu", "*CCC(=O)O", SIDECHAIN, "glutamate"),
    Group("Asn", "*CC(N)=O", SIDECHAIN, "asparagine"),
    Group("Gln", "*CCC(N)=O", SIDECHAIN, "glutamine"),
    Group("Lys", "*CCCCN", SIDECHAIN, "lysine aminobutyl"),
    Group("Arg", "*CCCNC(N)=N", SIDECHAIN, "arginine 3-guanidinopropyl"),
    Group("His", "*Cc1c[nH]cn1", SIDECHAIN, "histidine 1H-imidazol-4-ylmethyl"),
    Group("Phe", "*Cc1ccccc1", SIDECHAIN, "phenylalanine benzyl"),
    Group("Tyr", "*Cc1ccc(O)cc1", SIDECHAIN, "tyrosine 4-hydroxybenzyl"),
    Group("Trp", "*Cc1c[nH]c2ccccc12", SIDECHAIN, "tryptophan 1H-indol-3-ylmethyl"),
    # --- Nucleobases (N-linked, as in nucleosides) ---
    Group("Adenin-9-yl", "*n1cnc2c(N)ncnc21", NUCLEOBASE, "adenine A"),
    Group("Guanin-9-yl", "*n1cnc2c1nc(N)[nH]c2=O", NUCLEOBASE, "guanine G"),
    Group("Cytosin-1-yl", "*n1ccc(N)nc1=O", NUCLEOBASE, "cytosine C"),
    Group("Thymin-1-yl", "*n1cc(C)c(=O)[nH]c1=O", NUCLEOBASE, "thymine T"),
    Group("Uracil-1-yl", "*n1ccc(=O)[nH]c1=O", NUCLEOBASE, "uracil U"),
]


def categories() -> List[str]:
    """Category names in library order, de-duplicated."""
    seen: List[str] = []
    for group in GROUPS:
        if group.category not in seen:
            seen.append(group.category)
    return seen


def search(query: str, category: str = "") -> List[Group]:
    """Filter the library by free-text query (label or alias) and category."""
    needle = query.strip().lower()
    result = []
    for group in GROUPS:
        if category and group.category != category:
            continue
        if (
            needle
            and needle not in group.label.lower()
            and needle not in group.aliases.lower()
        ):
            continue
        result.append(group)
    return result

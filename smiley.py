import os,re

class SmileyAction(object):
    def __init__(self,path="smileys.txt"):
        """ Initialise le dictionnaire de smileys """
        # Création de l'élément racine
        self.smileys = dict()
        # Ouverture du fichier
        with open(path,encoding="utf-8-sig") as _file : 
            for _n,_line in enumerate(_file) : 
                _data = _line.rstrip().split("\t")
                # On ajoute la ligne courante dans de dico de smileys
                _sm = _data[1].strip() # Smiley
                _occ = _data[2] # Occurences
                if _sm not in self.smileys.keys() and len(_sm):
                    self.smileys[_sm]=_occ
        # Création du dictionnaire de résultats
        self.results = dict.fromkeys(self.smileys.keys(),0)
        # Création et ouverture du fichier de log
        self.logFile = open("log_smiley_tmp.txt","w")
        
    def do(self,line,index):
        """ Test si les mots line est dans l'arbre liwc"""
        # Regex pour éliminer les URL
        re_url   = re.compile("http[s]?://[^:/]+(?::\d+)?(?:/[^?]+)?(?:\?[^#]+)?(?:#.+)?",re.IGNORECASE)
        re_asp   = re.compile("/ASPFront/com/edf/asp/portlets/generationpdf/getFacturePDF.do[?]numFact=[0-9]+&factQE=[0-9]*&dateFactureQE=[0-9]{2}/[0-9]{2}/[0-9]{4}&&origineFact=DF",re.IGNORECASE)
        re_mail  = re.compile("[\w.-]+@[\w-]+\.\w{2,6}",re.IGNORECASE)
        re_date1 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d")
        re_date2 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d\d")
        re_date3 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])")
        _newline = re.sub(re_url,"\t[URL]\t",line)
        _newline = re.sub(re_asp,"\t[ASP]\t",_newline)
        _newline = re.sub(re_mail,"\t[MAIL]\t",_newline)
        _newline = re.sub(re_date1,"\t[DATE]\t",_newline)
        _newline = re.sub(re_date2,"\t[DATE]\t",_newline)
        _newline = re.sub(re_date3,"\t[DATE]\t",_newline)
        # On découpe la ligne en mots
        for _sm in self.results.keys() : 
            if _newline.find(_sm) > -1 : 
                self.logFile.write("{}\t\t - #{}:{}\n".format(_sm,index,_newline))
                #Le smiley est dans la ligne
                self.results[_sm] += 1
                    
    def finalize(self,fileName):
        """ Création du fichier de résultat """
        # Création du nom de fichier
        self.logFile.close()
        _filePath = "smiley_{}.csv".format(fileName)
        with open(_filePath,"w", encoding="utf-8-sig") as file: 
            for _k,_c in self.results.items() : 
                if _c > 0 :
                    _output = "{}\t{}\n".format(_k,_c)
                    file.write(_output)

        # Test d'existence
        return os.path.exists(_filePath)
        
    def saveUnique(smileydata):
        with open("smileyfinal.txt",'w') as file :
            for _k,_v in smileydata.iteritems() : 
                _line = _k+'\t'+_v+'\n'
                file.write(_line)

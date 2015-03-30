#-------------------------------------------------------------------------------
# Name:        split
# Purpose:
#
# Author:      Irina
#
# Created:     14/02/2015
# Copyright:   (c) Irina 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os,sys
import re
import csv
import datetime
import nltk
from liwc   import LiwcAction
from smiley import SmileyAction

class LineData(object):
    """ Traite les informations relative à une ligne """
    
    # keys = ['date','id','ref','talk','theme','satisf','civ','nom','prenom'] # Correspond aux en-têtes des colones
    keys = ['date','id','dialogId','interactionId','civ','talk','answer']
    
    def __init__(self,listItem):
        """ Creation d'un LineData a partir d'une liste de str"""
        self.keys = ['date','id','dialogId','interactionId','civ','talk','answer'] #liste d'entetes de colonnes
        # Erreur si le nombre de colonne ne correspond pas au nombre de cles
        if len(listItem) != len(self.keys) :
            print(listItem)
            print(len(listItem),len(self.keys))
            raise Exception("Nombre de colones incorrect")

        # Pour chaque cle, on cree dynamiquement l'attribut correspondant avec la valeur correspondante
        for _i,_k in enumerate(self.keys):
            setattr(self,_k,listItem[_i])
        
        self.duplicates = 0
        
    def do_clean(self):
        """ Netoyage du text utilisateur"""
        # Regex pour éliminer les URL
        re_url   = re.compile("http[s]?://[^:/]+(?::\d+)?(?:/[^?]+)?(?:\?[^#]+)?(?:#.+)?",re.IGNORECASE)
        re_asp   = re.compile("/ASPFront/com/edf/asp/portlets/generationpdf/getFacturePDF.do[?]numFact=[0-9]+&factQE=[0-9]*&dateFactureQE=[0-9]{2}/[0-9]{2}/[0-9]{4}&&origineFact=DF",re.IGNORECASE)
        # Regex pour éliminer les adresse mail
        re_mail  = re.compile("[\w.-]+@[\w-]+\.\w{2,6}",re.IGNORECASE)
        # Regex pour éliminer les dates
        re_date1 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d")
        re_date2 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d\d")
        re_date3 = re.compile("(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])")
        _newline = re.sub(re_url,"\t[URL]\t",self.talk)
        _newline = re.sub(re_asp,"\t[ASP]\t",_newline)
        _newline = re.sub(re_mail,"\t[MAIL]\t",_newline)
        _newline = re.sub(re_date1,"\t[DATE]\t",_newline)
        _newline = re.sub(re_date2,"\t[DATE]\t",_newline)
        _newline = re.sub(re_date3,"\t[DATE]\t",_newline)
        self.talk_clean=_newline
        # On ajoute la nouvelle colonne a la liste des cles (qui va servir à créer une colonne suplémentaire en sortie)
        if 'talk_clean' not in self.keys:          self.keys.append('talk_clean')

    def do_tokenize(self):
        """ Applique les tokenizers sur les donnees"""
        self.sentences = nltk.sent_tokenize(self.talk_clean)
        # On ajoute la nouvelle colonne a la liste des cles (qui va servir à créer une colonne suplémentaire en sortie)
        self.words = re.split('\W+', self.talk_clean, flags = re.UNICODE)
        self.words = list(filter(('').__ne__,self.words))
        self.wordcount = len(self.words)
        # On ajoute les nouvelles colones a la liste des cles
        if 'sentences' not in self.keys:          self.keys.append('sentences')
        if 'words' not in self.keys:              self.keys.append('words')
        if 'wordcount' not in self.keys:          self.keys.append('wordcount')

    def do_format(self):
        """ Met les donnees dans un format exploitable"""
        self.outputsentences = "\n".join(self.sentences)
        # On met les dates au format jjmmaaaa et entre balises pour Lexico3
        _date = self.date[8:10]+self.date[5:7]+self.date[0:4]
        self.outputdate = '<jjmmaaaa='+_date+'>' 
        # On ajoute les nouvelles colones a la liste des cles
        if 'outputsentences' not in self.keys:    self.keys.append('outputsentences')
        if 'outputdate' not in self.keys:         self.keys.append('outputdate')
        if 'duplicates' not in self.keys:         self.keys.append('duplicates')

class FileData(object):
    """ Assure la gestion d'une liste de LineData, correspondant a chaque ligne du fichier"""
    
    def __init__(self,dirPath,separator = '|'):
        """ Charge le fichier dirPath et cree les LineData a partir des lignes """
        self.lines = list()
        self.separator = separator
        self.idMap = dict() # Dico[idUser] = [index des posts,]
        # self.file = datetime.datetime.now().strftime('%y%m%d-%H%M')
        self.file = os.path.basename(dirPath)
        for _fileName in os.listdir(dirPath):
            # Ouverture du fichier
            # L'encodage "utf-8-sig" correspond a UTF avec BOM
            _filePath = os.path.join(dirPath,_fileName)
            with open(_filePath, newline='', encoding="utf-8-sig") as _csvfile : 
                # Parcours du fichier
                _csvreader = csv.reader(_csvfile, delimiter='|')
                for _n,_line in enumerate(_csvreader) :
                    # On ajoute toutes les lignes sauf la premiere
                    if _n == 0 : pass
                    else : self.append(_line)
            self.idMap.clear()
            print (_filePath,_n,'\n\tLignes parcourues')
        print('-----------------------------------------------------------')
    
    def append(self,line):
        """ Cree un LineData a partir de la ligne et l'ajoute a la liste"""
        # On cree le LineData a partir des elements de la ligne
        try : 
            _data=LineData(line)
            
            if _data.id not in self.idMap.keys():
                self.idMap[_data.id] = list()
            for _existant in self.idMap[_data.id] :
                if _existant.talk == _data.talk :
                    # C'est un doublon, on sort
                    _existant.duplicates += 1
                    return False
            # Il n'y a pas eu de doublon, on ajoute
            self.idMap[_data.id].append(_data)
            
            self.lines.append(_data)   
        # En cas d'erreur on affiche l'erreur
        except Exception as err:            
            print(err)
            raise
        # Affichage du compte
        return True
                
    def do_loop(self):
        """ Parcours des lignes et application des opérations """
        # ---------- INITIALISATION DES ACTIONS ----------------
        # Compte des doublons
        _nbLinesWithDuplicates   = sum(l.duplicates for l in self.lines)
        _nbTotalDuplicates       = sum(1 for l in self.lines if l.duplicates > 0)
        _duplicatesRatio         = float(_nbLinesWithDuplicates)/float(len(self.lines))
        print('Lignes analysees          :',len(self.lines))
        print('Lignes ayant des doublons :',_nbLinesWithDuplicates)
        print('Nombre total de doublons  :',_nbTotalDuplicates)
        print('Taux de doublons          : {:.3f}%'.format(_duplicatesRatio) ) # {:.3f} est pour dire que le resultat doit etre en "float" comprenant 3 chiffres apres la virgule
        print('-----------------------------------------------------------')
        _countSentences = 0
        _notEmpty = 0
        # Comptage des smileys
        # en fonction de résultats qu'on a besoin, on peut commenter ou descommenter
        smiley  = SmileyAction(self.file)
        # liwc    = LiwcAction(self.file)
        # ---------------- PARCOURS DES LIGNES --------------------
        for _n,_line in enumerate(self.lines) :
            # Nettoyage du texte utilisateur
            _line.do_clean()
            # Appel du Tokenizer
            _line.do_tokenize()
            if len(_line.talk_clean.rstrip()) : _notEmpty += 1
            _countSentences += len(_line.sentences) # Ajout du nombre de phrases 
            # Formattage des lignes
            _line.do_format()
            # smiley.do(_line.talk_clean,_line.dialogId)
            smiley.do(_line.talk_clean,_line.interactionId)
            # liwc.do(_line.talk_clean,_n)
            if _n % 100 == 0: print('{:.2f}%'.format(_n/float(len(self.lines))), end='\r')
                    
        # ------------- FINALISATION DES ACTIONS ----------------
        print('smiley :',smiley.finalize())
        # print('liwc :',liwc.finalize())
        print('Nombre total de phrases  :',_countSentences)
        print('Nombre lignes non vides  :',_notEmpty)
        _dialogIds = set(l.dialogId for l in self.lines)
        print('Nombre de dialogId       :',len(_dialogIds))
        print('-----------------------------------------------------------')
        # with open(self.file+"_overview.txt","w") as _overview :
            # _overview.write('Lignes analysees          :{}\n'.format(len(self.lines)))
            # _overview.write('Lignes ayant des doublons :{}\n'.format(_nbLinesWithDuplicates))
            # _overview.write('Nombre total de doublons  :{}\n'.format(_nbTotalDuplicates))
            # _overview.write('Taux de doublons          : {:.3f}%\n'.format(_duplicatesRatio) )
            # _overview.write('Nombre total de phrases   :{}\n'.format(_countSentences))
            # _overview.write('Nombre lignes non vides   :{}\n'.format(_notEmpty))
            # _overview.write('Nombre de dialogId        :{}\n'.format(len(_dialogIds)))
    
    def do_output(self,filePath,*col):
        """Cree un fichier resultat contenant uniquement les colonnes specifiees pour chaque ligne """
        # Creation du fichier
        # L'encodage "utf-8-sig" correspond a UTF avec BOM
        with open(filePath,'w',encoding="utf-8-sig") as _file :
            # Pour chaque ligne
            for _l in self.lines :
                # Pour chaque colonne specifiee
                #_buffer = self.separator.join(list(str(getattr(_l,_c,"")) for _c in col))
                _buffer = ";".join(list('"{}"'.format(str(getattr(_l,_c,""))) for _c in col))
                _buffer+= "\n"
                _file.write(_buffer)
        # On verifie que le fichier a bien ete cree
        if os.path.exists(filePath) : print("Fichier cree",filePath)
        else : print("Oups, pas de fichier")
                        
#myDir = "D:\\Python32\\Test"
myDir = "E:\\Python32\\CSVciv\\01"
data = FileData(myDir)
data.do_loop()

#descommenter pour avoir un .csv de sortie

# if len(data.lines) :
   # data.do_output(os.path.basename(myDir)+"_output.txt",'date','id','dialogId','interactionId','civ','talk','talk_clean','words','wordcount',
        # 'answer',"duplicates")
'''
print('--> pour avoir une sortie: data.do_output("F:\\result_test.txt","talk","outputsentences")')
print('--> liste des colonnes possibles\n\t-','\n\t- '.join(data.lines[0].keys))
'''   

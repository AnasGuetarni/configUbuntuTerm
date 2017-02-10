# -*- coding:Utf-8 -*-

import pygtk

pygtk.require("2.0")

import gtk

import os


class DocumentOuvert():

    "Objet qui contient des informations sur un fichier ouvert"

    def __init__(self):

        self.chemin = ''

        self.aSauvegarder = False

        self.zoneTexteDocument = None


class PyGtkApp:

    def __init__(self):

        #Création de la fenêtre principale à partie d'un fichier glade

        interface = gtk.Builder()

        interface.add_from_file('fenetre.glade')

        

        self.fenetre = interface.get_object("fenetre")

        self.barresDefilement = interface.get_object('barresDefilement')

        interface.connect_signals(self)

        

        self.fenetre.maximize()

        

        self.documents = [] #Liste des documents ouverts

        self.documentActif = None #Le document actif (objet DocumentOuvert())

        

    def detruireFen(self, widget, evenement):

        "Lorsque la fenêtre est détruite"

        if self.documentActif != None:

            if not self.fermer(None) == False:

                return False #Si le document est bien fermé, on peut fermer la fenêtre

        else:

            return False #Si aucun document n'est actif, on peut aussi la fermer

        return True #Sinon, on la laisse ouverte

    

    def aPropos(self, widget):

        "Dialogue À propos"

        pixbuf = gtk.gdk.pixbuf_new_from_file("editeurDeTexteIco.png")

        aPropos = gtk.AboutDialog()

        aPropos.set_icon_from_file("editeurDeTexteIco.png")

        aPropos.set_name("Éditeur de texte")

        aPropos.set_version("1.0")

        aPropos.set_copyright("Copyright © 2009, tous droits réservés")

        aPropos.set_comments(aPropos.get_name() + " " + aPropos.get_version() +" est un éditeur de texte basique.")

        aPropos.set_license("Copyright © 2009 antoyo\n\nThis program is free software; you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation; either version 2 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License along\nwith this program; if not, write to the Free Software Foundation, Inc.,\n51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.")

        auteurs = ["Antoyo"]

        aPropos.set_authors(auteurs)

        aPropos.set_logo(pixbuf)

        reponse = aPropos.run()

        aPropos.destroy()

    

    def fermer(self, widget):

        "Fermeture d'un fichier" #Dans cette fonction, si le retour est False, cela indique qu'il n'y a pas eu de fermeture

        if self.documentActif != None: #S'il y a un document actif

            if self.documentActif.aSauvegarder: #Si il est modifié

                #On crée un boîte de dialogue pour demander à l'utilisateur s'il veut enregistrer les modifications ou non ou bien annuler la fermeture

                fermetureDialogue = gtk.Dialog("Enregistrer", self.fenetre, 0, (gtk.STOCK_YES, gtk.RESPONSE_YES, gtk.STOCK_NO, gtk.RESPONSE_NO, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

                

                etiquette = gtk.Label('Voulez-vous enregistrer les modifications ?')

                boiteH = gtk.HBox()

                fermetureDialogue.vbox.pack_start(boiteH, False)

                stock = gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)

                boiteH.pack_start(stock, False)

                boiteH.pack_start(etiquette, False)

                

                fermetureDialogue.show_all()

                

                reponse = fermetureDialogue.run()

                if reponse == gtk.RESPONSE_YES:

                    if self.enregistrer(None):

                        #Si l'utilisateur appuie sur Oui et qu'il enregistre le document, on peut le fermer

                        self.documentActif.zoneTexteDocument.destroy()

                        

                        self.documents.remove(self.documentActif)

                        self.documentActif = None

                    else:

                        #S'il ne l'enregistre pas, on ferme la boîte de dialogue

                        fermetureDialogue.destroy()

                        return False

                    self.fenetre.set_title('Éditeur de texte en PyGtk') #On remet le titre à la fenêtre

                elif reponse == gtk.RESPONSE_NO:

                    #S'il appuie sur Non, on ferme le document sans enregistrer

                    self.documentActif.zoneTexteDocument.destroy()

                    

                    self.documents.remove(self.documentActif)

                    self.documentActif = None

                    self.fenetre.set_title('Éditeur de texte en PyGtk')

                elif reponse == gtk.RESPONSE_CANCEL:

                    #S'il appuie sur Annuler, on fermer seulement la boîte de dialogue

                    fermetureDialogue.destroy()

                    return False

                fermetureDialogue.destroy()

            else:

                self.documentActif.zoneTexteDocument.destroy()

                self.documents.remove(self.documentActif)

                self.documentActif = None

                self.fenetre.set_title('Éditeur de texte en PyGtk')

        else:

            self.afficherAvertissement("Il n'y a aucun document ouvert.")

    

    def nouveau(self, widget):

        "Création d'un nouveau document"

        if self.documentActif == None: #On le crée seulement s'il n'y en a pas déjà un d'ouvert

            #Création d'un objet DocumentOuvert() sans chemin

            nouveau = DocumentOuvert()

            nouveau.chemin = ''

            nouveau.ASauvegarder = False

            #Le chemin vaut '' et il n'est pas à sauvegarder

            self.documents.append(nouveau) #On l'ajoute à la liste

            self.documentActif = nouveau #Et c'est le document actif

        

            nouveau.zoneTexteDocument = gtk.TextView() #On crée une nouvelle zone de texte

            tampon = nouveau.zoneTexteDocument.get_buffer()

            tampon.connect("changed", self.fichierModifie) #On récupère le tampon pour savoir quand il est modifié

            self.barresDefilement.add(nouveau.zoneTexteDocument)

            nouveau.zoneTexteDocument.show()

        

            self.definirTitre()

        else:

            self.afficherAvertissement("Il y a déjà un document ouvert.")

    

    def fichierModifie(self, widget):

        #Si un fichier est modifié, on change son status et le titre de la fenêtre

        self.documentActif.aSauvegarder = True

        self.definirTitre()

    

    def definirTitre(self):

        titre = ''

        if self.documentActif.chemin != '':

            #Si un document est ouvert, on affiche son nom

            titre = os.path.basename(self.documentActif.chemin)

        else:

            #Si c'est un nouveau document, on affiche 'Nouveau document'

            titre = 'Nouveau document'

        if self.documentActif.aSauvegarder:

            #S'il est modifié, on ajoute une étoile

            titre = '*' + titre

        self.fenetre.set_title(titre)

    

    def enregistrer(self, widget):

        #Retourne False si l'utilisateur n'effectue pas la sauvegarde, sinon retourne True

        if self.documentActif != None:

            if self.documentActif.aSauvegarder:

                if self.documentActif.chemin == '':

                    #Si un document est ouvert, modifié et n'existe pas dans l'ordinateur, on affiche la boîte de dialogue Enregistrer sous

                    sauvegarderFichierDialogue = gtk.FileChooserDialog("Enregistrer sous...", self.fenetre, gtk.FILE_CHOOSER_ACTION_SAVE, ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK)))

                    sauvegarderFichierDialogue.set_do_overwrite_confirmation(True)

                    reponse = sauvegarderFichierDialogue.run()

                    

                    if reponse == gtk.RESPONSE_OK:

                        nomFichier = sauvegarderFichierDialogue.get_filename()

                        self.documentActif.chemin = nomFichier

                        sauvegarderFichierDialogue.destroy()

                    elif reponse == gtk.RESPONSE_CANCEL:

                        sauvegarderFichierDialogue.destroy()

                        return False

                if self.documentActif.chemin != '':

                    fichier = open(self.documentActif.chemin, 'w') #On ouvre le fichier

                    

                    #On obtient le texte de la zone de texte

                    tampon = self.documentActif.zoneTexteDocument.get_buffer()

                    debut = tampon.get_start_iter()

                    fin = tampon.get_end_iter()

                    texte = tampon.get_text(debut, fin, True)

                    

                    #On enregistre le fichier

                    fichier.write(texte)

                    fichier.close()

                    #Il n'est plus à sauvegarder, donc on change le titre (plus d'étoile)

                    self.documentActif.aSauvegarder = False

                    self.definirTitre()

                    return True

            else:

                if self.fenetre.get_title() == 'Nouveau document':

                    #Si le document n'est pas modifié, mais que c'est un nouveau document, on peut l'enregistrer

                    self.documentActif.aSauvegarder = True

                    if not self.enregistrer(None):

                        #Si l'utilisateur ne le sauvegarde pas

                        self.documentActif.aSauvegarder = False

            self.definirTitre()

        else:

            self.afficherAvertissement("Il n'y a aucun document ouvert.")

    

    def enregistrerSous(self, widget):

        if self.documentActif != None: #Si un document est ouvert

            #On enregistre des informations temporaires au cas où l'utilisateur annulerait la sauvegarde            

            cheminTemp = self.documentActif.chemin

            aSauvegarderTemp = self.documentActif.aSauvegarder

            

            #On change le chemin pour '' et aSauvegarde pour True pour que l'enregistrement se fasse dans un autre fichier (enregistrer sous)

            self.documentActif.chemin = ''

            self.documentActif.aSauvegarder = True

            if not self.enregistrer(widget): #Si l'utilisateur annule l'enregistrement, on remet les informations d'avant

                self.documentActif.chemin = cheminTemp

                self.documentActif.aSauvegarder = aSauvegarderTemp

                self.definirTitre() #et on remet le titre (parce qu'on le change après l'enregistrement)

        else:

            self.afficherAvertissement("Il n'y a aucun document ouvert.")

    

    def quitter(self, widget, evenement = None):

        if self.documentActif != None:

            if not self.fermer(None) == False:

                #Si un document est ouvert, mais qu'il est fermé après, on quitter

                gtk.main_quit()

        else:

            #Si aucun document est ouvert, on quitte

            gtk.main_quit()

    def ouvrirFichier(self, nomFichier):
        #Cette méthode ressemble à la méthode self.nouveau()
        #Création d'un objet DocumentOuvert() avec chemin
        nouveau = DocumentOuvert()
        nouveau.chemin = nomFichier
        nouveau.ASauvegarder = False
        self.documents.append(nouveau)
        self.documentActif = nouveau
        nouveau.zoneTexteDocument = gtk.TextView()
        nouveau.zoneTexteDocument.show()
        self.barresDefilement.add(nouveau.zoneTexteDocument)
        tampon = nouveau.zoneTexteDocument.get_buffer()
        fichier = open(nomFichier, 'r')
        texteListe = fichier.readlines()
        texte = ''.join(texteListe)
        fichier.close()

        #Comme on doit changer le texte pour celui du fichier, il faut bien faire attention à connecter le signal 'changed' APRÈS de l'avoir changer pour pas que l'attribut aSauvegarder devienne True
        tampon.set_text(texte)
        tampon.connect("changed", self.fichierModifie)
        self.definirTitre()
    
    def ouvrirFichierDialogue(self, widget):
        continuer = False
        if self.documentActif != None:
            if not self.fermer(None) == False:
                #Si le document ouvert se ferme, on peut ouvrir la boîte de dialogue
                continuer = True
        else:
            #Si aucun document est ouvert, on peut ouvrir la boîte de dialogue
            continuer = True
        if continuer:
            ouvrirFichierDialogue = gtk.FileChooserDialog("Ouverture de fichiers", self.fenetre, gtk.FILE_CHOOSER_ACTION_OPEN, ((gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)))
            reponse = ouvrirFichierDialogue.run()
            if reponse == gtk.RESPONSE_OK:
                nomFichier = ouvrirFichierDialogue.get_filename()
                #On essaie d'ouvrir le fichier pour savoir s'il existe
                try:
                    fichier = open(nomFichier)
                except:
                    #Dans le cas où l'utilisateur aurait taper le nom du fichier et que celui-ci n'existerait pas, on affiche une erreur
                    self.afficherErreur('Le fichier <b>' + os.path.basename(nomFichier) + '</b> n\'existe pas.', True)
                else:
                    #S'il existe, on l'ouvre
                    fichier.close()
                    self.ouvrirFichier(nomFichier)
            ouvrirFichierDialogue.destroy()

    def afficherInformation(self, texte, use_markup = False):
        "Affiche une information (non utilisée)"
        if use_markup:
            #Si use_markup vaut True, on insère le texte avec set_markup()
            infoDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
            infoDialogue.set_markup(texte)
        else:
            infoDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, texte)
        infoDialogue.set_title("Information")
        infoDialogue.run()
        infoDialogue.destroy()

    def afficherAvertissement(self, texte, use_markup = False):
        "Affiche un avertissement"
        if use_markup:
            avertissementDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK)
            avertissementDialogue.set_markup(texte)
        else:
            avertissementDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, texte)
        avertissementDialogue.set_title("Avertissement")
        avertissementDialogue.run()
        avertissementDialogue.destroy()

    def afficherErreur(self, texte, use_markup = False):
        "Affiche une erreur"
        if use_markup:
            erreurDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
            erreurDialogue.set_markup(texte)
        else:
            erreurDialogue = gtk.MessageDialog(self.fenetre, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, texte)
        erreurDialogue.set_title("Erreur")
        erreurDialogue.run()
        erreurDialogue.destroy()
        erreurDialogue.destroy()

PyGtkApp()
gtk.main()

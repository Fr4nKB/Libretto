#stuff
TOTCFU = [120, 180, 300]
MAXNAMELEN = 76 #desired length + 1

#gui
init_unipi = ['USERNAME', 'PASSWORD', 'THESIS VALUE', '30L VALUE']
init_man = ['THESIS VALUE', '30L VALUE']
fields = ['CORSO', 'VOTO', 'CFU', 'DATA (dd/mm/yyyy)']
phrase = ["La media ponderata è ", "Media con solo 18 d'ora in poi: ", "Media con solo 30L d'ora in poi: "]

#sites and payload to load grades from unipi servers
urls = ['https://www.studenti.unipi.it/auth/Logon.do', 'https://www.studenti.unipi.it/auth/studente/HomePageStudente.do', 'https://www.studenti.unipi.it/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Carriera']
payload1 = {
    'shib_idp_ls_exception.shib_idp_session_ss': "",
    'shib_idp_ls_success.shib_idp_session_ss': "true",
    'shib_idp_ls_value.shib_idp_session_ss': "",
    'shib_idp_ls_exception.shib_idp_persistent_ss': "",
    'shib_idp_ls_success.shib_idp_persistent_ss': "true",
    'shib_idp_ls_value.shib_idp_persistent_ss': "",
    'shib_idp_ls_supported': "true",
    '_eventId_proceed': "" 
}

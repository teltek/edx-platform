

(function (globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function (n) {
    var v=(n != 1);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  
  /* gettext library */

  django.catalog = {
    "%(type)s Component Template Menu": "Men\u00fa de %(type)s modelo de compo\u00f1ente", 
    "- Sortable": "- Clasificable", 
    "Abbreviation": "Abreviatura", 
    "Activate": "Activar", 
    "Add Additional Signatory": "Engadir Asinante Adicional", 
    "Add Component:": "Engadir compo\u00f1ente:", 
    "Add New Component": "Engade unha nova compo\u00f1ente", 
    "Admin": "Persoa administradora", 
    "Advanced": "Avanzado", 
    "All Groups": "Todos os grupos", 
    "All Rights Reserved": "Todos os dereitos reservados", 
    "Are you sure you want to delete this update?": "Tes a certeza de quereres eliminar esta actualizaci\u00f3n?", 
    "Are you sure you wish to delete this item. It cannot be reversed!\n\nAlso any content that links/refers to this item will no longer work (e.g. broken images and/or links)": "Tes a seguranza de quereres eliminar este elemento? Non se vai poder recuperar!\n\nPara al\u00e9n disto, calquera contido que ligue ou se refira a este elemento non funcionar\u00e1 m\u00e1is (por exemplo, imaxes e / ou ligaz\u00f3ns rotas)", 
    "Are you sure?": "Est\u00e1s seguro/a?", 
    "Assignment Type Name": "Nome do Tipo de Tarefa", 
    "Cancel": "Cancelar", 
    "Cannot delete when in use by a unit": "Non se pode eliminar mentres estea en uso por unha unidade", 
    "Caution: The last published version of this unit is live. By publishing changes you will change the student experience.": "Coidado: A \u00faltima versi\u00f3n publicada desta unidade est\u00e1 sendo empregada. Se publicas os cambios podes afectar \u00e1 experiencia dos estudantes.", 
    "Certificate Details": "Detalles do certificado", 
    "Certificate Information": "Informaci\u00f3n do Certificado", 
    "Certificate Name": "Nome do Certificado", 
    "Certificate Signatories": "Asinantes do Certificado", 
    "Choose File": "Elixe un ficheiro", 
    "Choose mode": "Escoller modo", 
    "Click to add a new %(xblock_type)s": "Preme para engadir un novo %(xblock_type)s", 
    "Collapse Instructions": "Contraer instruci\u00f3ns", 
    "Collapse/Expand this %(xblock_type)s": "Colapsar/Expandir este %(xblock_type)s", 
    "Commentary": "Comentario", 
    "Common Problem Types": "Tipos de Problema Com\u00fan", 
    "Configure": "Configurar", 
    "Confirm": "Confirmar", 
    "Contains staff only content": "Cont\u00e9n contido exclusivo para o staff", 
    "Content Group ID": "ID do Grupo de Contido", 
    "Content Group Name": "Nome do Grupo de Contido", 
    "Country": "Pa\u00eds", 
    "Course": "Curso", 
    "Course Number": "N\u00famero do curso", 
    "Course Number Override": "Ignorar o n\u00famero do curso", 
    "Course Title": "T\u00edtulo do curso", 
    "Course Title Override": "Ignorar o t\u00edtulo do curso", 
    "Course title": "T\u00edtulo do curso", 
    "Create": "Crear", 
    "Current Role:": "Rol actual:", 
    "Dashboard": "Panel", 
    "Date Added": "Data engadida", 
    "Deactivate": "Desactivar", 
    "Delete": "Eliminar", 
    "Delete File Confirmation": "Confirmaci\u00f3n de eliminaci\u00f3n do ficheiro", 
    "Delete the user, {username}": "Eliminar a persoa usuaria {username}", 
    "Delete this asset": "Borra este recurso", 
    "Delete \u201c<%= name %>\u201d?": "Eliminar \u201c<%= name %>\u201d?", 
    "Deleting": "Eliminando", 
    "Deleting a textbook cannot be undone and once deleted any reference to it in your courseware's navigation will also be removed.": "A eliminaci\u00f3n dun libro de texto non se pode desfacer. Unha vez eliminado, calquera referencia a el na dentro dos teus materiais do curso tam\u00e9n se retirar\u00e1.", 
    "Deprecated": "Desprezar", 
    "Description": "Descrici\u00f3n", 
    "Description of the certificate": "Descrici\u00f3n do certificado", 
    "Display Name": "Amosar Nome", 
    "Drag and drop or click here to upload video files.": "Arrastra e solta ou preme aqu\u00ed para cargar ficheiros de v\u00eddeo.", 
    "Drag to reorder": "Arrastra para reordear", 
    "Edit": "Editar", 
    "Editor": "Editor", 
    "Email": "Enderezo de correo electr\u00f3nico", 
    "Email Address": "Enderezo de correo electr\u00f3nico", 
    "Error": "Erro", 
    "Error:": "Erro:", 
    "Expand Instructions": "Estender instruci\u00f3ns", 
    "Files must be in JPEG or PNG format.": "Os ficheiros deben estar en formato JPEG ou PNG.", 
    "Forgot password?": "Esqueciches o teu contrasinal?", 
    "Full Name": "Nome completo", 
    "Gender": "Sexo", 
    "General": "Xeral", 
    "Grace period must be specified in HH:MM format.": "O per\u00edodo de graza d\u00e9bese especificar no normato HH:MM.", 
    "Graded as:": "Cualificado como:", 
    "Heading 1": "Cabeceira 1", 
    "Hide Annotations": "Ocultar anotaci\u00f3ns", 
    "ID": "ID", 
    "Key should only contain letters, numbers, _, or -": "A clave s\u00f3 debe conter letras, n\u00fameros, _ ou -", 
    "Language": "Lingua", 
    "List of uploaded files and assets in this course": "Lista de ficheiros e recursos cargados neste curso", 
    "Load Another File": "Cargar outro ficheiro", 
    "Loading": "Cargando", 
    "Lock this asset": "Bloquea este recurso", 
    "Lock/unlock file": "Bloquear/desbloquear ficheiro", 
    "My Notes": "As mi\u00f1as notas", 
    "Name": "Nome", 
    "Name of the certificate": "Nome do certificado", 
    "Next": "Seguinte", 
    "No description available": "Non hai descrici\u00f3n dispo\u00f1ible", 
    "None": "Ning\u00fan", 
    "Not Graded": "Non cualificado", 
    "OK": "OK", 
    "Only <%= fileTypes %> files can be uploaded. Please select a file ending in <%= fileExtensions %> to upload.": "S\u00f3 se poden cargar os ficheiros <%= fileTypes %>. Por favor, selecciona para cargar un ficheiro que acabe en <%= fileExtensions %>.", 
    "Open Calculator": "Abrir calculadora", 
    "Open/download this file": "Abrir/descargar este ficheiro", 
    "Organization": "Organizaci\u00f3n", 
    "Other": "Outro", 
    "Password": "Contrasinal", 
    "Pause": "Pausar", 
    "Please address the errors on this page first, and then save your progress.": "Por favor, primeiro corrixe os erros nesta p\u00e1xina e despois garda o teu progreso.", 
    "Please do not use any spaces in this field.": "Por favor, non uses espazo ning\u00fan neste campo.", 
    "Please enter an integer between 0 and 100.": "Por favor, introduce un n\u00famero enteiro entre 0 e 100.", 
    "Please enter an integer greater than 0.": "Por favor, introduce un n\u00famero enteiro maior que 0.", 
    "Please enter non-negative integer.": "Por favor, introduce un n\u00famero enteiro non negativo.", 
    "Preferred Language": "Lingua preferida", 
    "Preview": "Vista previa", 
    "Preview Certificate": "Previsualizar certificado", 
    "Previous": "Anterior", 
    "Public": "P\u00fablico", 
    "Publish": "Publicar", 
    "Release Status:": "Estado de Liberaci\u00f3n:", 
    "Released:": "Liberado:", 
    "Remove": "Eliminar", 
    "Reply to Annotation": "Contestar \u00e1 anotaci\u00f3n", 
    "Required field.": "Campo obrigatorio", 
    "Save": "Gardar", 
    "Save Changes": "Gardar cambios", 
    "Save changes": "Gardar cambios", 
    "Saving": "A gardar", 
    "Scheduled:": "Datado:", 
    "Search": "Buscar", 
    "Section": "Secci\u00f3n", 
    "Send notification to mobile apps": "Enviar notificaci\u00f3n a apps m\u00f3biles", 
    "Settings": "Configuraci\u00f3n", 
    "Show Annotations": "Amosar anotaci\u00f3ns", 
    "Specify an alternative to the official course title to display on certificates. Leave blank to use the official course title.": "Especifica unha alternativa ao t\u00edtulo oficial do curso para amosar nos certificados. Deixao baleiro para empregar o t\u00edtulo oficial do curso.", 
    "Staff": "Persoal", 
    "Status": "Estado", 
    "Student": "Estudante", 
    "Studio's having trouble saving your work": "Studio ten problemas para gardar o teu traballo", 
    "Studio:": "Estudio:", 
    "Submit": "Enviar", 
    "Submitted": "Enviado", 
    "The course must have an assigned start date.": "O curso debe ter unha data de comezo asingada.", 
    "The enrollment end date cannot be after the course end date.": "A data de inscrici\u00f3n non pode ser posterior \u00e1 data de finalizaci\u00f3n do curso.", 
    "The enrollment start date cannot be after the enrollment end date.": "A data de comezo da inscrici\u00f3n non pode ser posterior \u00e1 data de finalizaci\u00f3n da inscrici\u00f3n.", 
    "There is invalid code in your content. Please check to make sure it is valid HTML.": "Hai un c\u00f3digo non v\u00e1lido no teu contido. Por favor, comproba que o HTML \u00e9 v\u00e1lido", 
    "There was an error during the upload process.": "Produciuse un erro durante o proceso de carga.", 
    "There was an error with the upload": "Produciuse un erro coa carga", 
    "There's already another assignment type with this name.": "Xa hai outro tipo de tarefa con ese nome.", 
    "This action cannot be undone.": "Esta acci\u00f3n non se pode desfacer.", 
    "This content group is used in one or more units.": "Este grupo de contido \u00e9 usado nunha ou m\u00e1is unidades", 
    "This content group is used in:": "Este grupo de contido \u00e9 empregado en:", 
    "This is the name of the group": "Este \u00e9 o nome do grupo", 
    "This link will open in a modal window": "A ligaz\u00f3n abrirase nunha xanela modal", 
    "This link will open in a new browser window/tab": "A ligaz\u00f3n abrirase nunha nova lapela do navegador", 
    "This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.": "Isto pode pasar por causa dun erro co noso servidor ou coa t\u00faa conexi\u00f3n a internet. Proba a actualizar a p\u00e1xina ou aseg\u00farate de que est\u00e1s conectado/a.", 
    "Title": "T\u00edtulo", 
    "Tools": "Ferramentas", 
    "Total Number": "N\u00famero Total", 
    "URL": "URL", 
    "Undo (Ctrl+Z)": "Desfacer (Ctrl+Z)", 
    "Unit": "Unidade", 
    "Unpublished units will not be released": "As unidades non publicadas non ser\u00e1n liberadas", 
    "Unscheduled": "Sen datar", 
    "Upload File": "Subir ficheiro", 
    "Upload New File": "Cargar un ficheiro novo", 
    "Upload a new PDF to \u201c<%= name %>\u201d": "Cargar un novo PDF en \u00ab<%= name %>\u00bb", 
    "Upload completed": "Carga completada", 
    "Upload your course image.": "Carga a t\u00faa imaxe para o curso.", 
    "Upload your first asset": "Carga o teu primeiro recurso", 
    "User": "Persoa usuaria", 
    "Username": "Nome de persoa usuaria", 
    "View": "Ver", 
    "View Course": "Ver curso", 
    "Volume": "Volume", 
    "We're sorry, there was an error": "Sent\u00edmolo, produciuse un erro", 
    "Web:": "Web:", 
    "Weight of Total Grade": "Ponderaci\u00f3n da Cualificaci\u00f3n Total", 
    "Year of Birth": "Ano de nacemento", 
    "You haven't added any assets to this course yet.": "A\u00ednda non tes engadido ning\u00fan recurso a este curso.", 
    "You haven't added any content to this course yet.": "A\u00ednda non engadiches ning\u00fan contido a este curso.", 
    "You must specify a name": "Debes especificar un nome", 
    "You!": "Ti!", 
    "You've made some changes": "Fixeches algunhas mudanzas.", 
    "You've made some changes, but there are some errors": "Fixeches algunhas mudanzas, mais hai alg\u00fans erros", 
    "Your changes have been saved.": "Gard\u00e1ronse os teus cambios", 
    "Your changes will not take effect until you save your progress.": "As t\u00faas mudanzas non ter\u00e1n efecto at\u00e9 que gardes o teu progreso.", 
    "Your changes will not take effect until you save your progress. Take care with key and value formatting, as validation is not implemented.": "Os teus cambios non ter\u00e1n efecto at\u00e9 que gardes o teu progreso. Ten coidado co formato da clave e do valor, xa que non se implementou validaci\u00f3n ningunha.", 
    "Your file has been deleted.": "Eliminouse o teu arquivo.", 
    "Your policy changes have been saved.": "Gard\u00e1ronse os cambios na pol\u00edtica.", 
    "a day": "un d\u00eda", 
    "about a minute": "arredor dun minuto", 
    "about a month": "arredor dun mes", 
    "about a year": "arredor dun ano", 
    "about an hour": "arredor dunha hora", 
    "anonymous": "an\u00f3nimo/a", 
    "close": "pechar", 
    "correct": "correcto", 
    "incorrect": "incorrecto", 
    "or": "ou", 
    "send an email message to {email}": "enviarlle unha mensaxe de correo electr\u00f3nico a {email}"
  };

  django.gettext = function (msgid) {
    var value = django.catalog[msgid];
    if (typeof(value) == 'undefined') {
      return msgid;
    } else {
      return (typeof(value) == 'string') ? value : value[0];
    }
  };

  django.ngettext = function (singular, plural, count) {
    var value = django.catalog[singular];
    if (typeof(value) == 'undefined') {
      return (count == 1) ? singular : plural;
    } else {
      return value[django.pluralidx(count)];
    }
  };

  django.gettext_noop = function (msgid) { return msgid; };

  django.pgettext = function (context, msgid) {
    var value = django.gettext(context + '\x04' + msgid);
    if (value.indexOf('\x04') != -1) {
      value = msgid;
    }
    return value;
  };

  django.npgettext = function (context, singular, plural, count) {
    var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
    if (value.indexOf('\x04') != -1) {
      value = django.ngettext(singular, plural, count);
    }
    return value;
  };
  

  django.interpolate = function (fmt, obj, named) {
    if (named) {
      return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
    } else {
      return fmt.replace(/%s/g, function(match){return String(obj.shift())});
    }
  };


  /* formatting library */

  django.formats = {
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \\\u00e1\\s H:i", 
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S", 
      "%Y-%m-%d %H:%M:%S.%f", 
      "%Y-%m-%d %H:%M", 
      "%Y-%m-%d", 
      "%m/%d/%Y %H:%M:%S", 
      "%m/%d/%Y %H:%M:%S.%f", 
      "%m/%d/%Y %H:%M", 
      "%m/%d/%Y", 
      "%m/%d/%y %H:%M:%S", 
      "%m/%d/%y %H:%M:%S.%f", 
      "%m/%d/%y %H:%M", 
      "%m/%d/%y"
    ], 
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y", 
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d", 
      "%m/%d/%Y", 
      "%m/%d/%y", 
      "%b %d %Y", 
      "%b %d, %Y", 
      "%d %b %Y", 
      "%d %b, %Y", 
      "%B %d %Y", 
      "%B %d, %Y", 
      "%d %B %Y", 
      "%d %B, %Y"
    ], 
    "DECIMAL_SEPARATOR": ",", 
    "FIRST_DAY_OF_WEEK": "1", 
    "MONTH_DAY_FORMAT": "j \\d\\e F", 
    "NUMBER_GROUPING": "0", 
    "SHORT_DATETIME_FORMAT": "d-m-Y, H:i", 
    "SHORT_DATE_FORMAT": "d-m-Y", 
    "THOUSAND_SEPARATOR": ".", 
    "TIME_FORMAT": "H:i", 
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S", 
      "%H:%M:%S.%f", 
      "%H:%M"
    ], 
    "YEAR_MONTH_FORMAT": "F \\d\\e Y"
  };

  django.get_format = function (format_type) {
    var value = django.formats[format_type];
    if (typeof(value) == 'undefined') {
      return format_type;
    } else {
      return value;
    }
  };

  /* add to global namespace */
  globals.pluralidx = django.pluralidx;
  globals.gettext = django.gettext;
  globals.ngettext = django.ngettext;
  globals.gettext_noop = django.gettext_noop;
  globals.pgettext = django.pgettext;
  globals.npgettext = django.npgettext;
  globals.interpolate = django.interpolate;
  globals.get_format = django.get_format;

}(this));


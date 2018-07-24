{
   'name' : "Activity",
   'version' : "1.0",
   'description' : 'Activity and link to hotel reservation',
   'author' : "Hout Ratha",
   'installable' : True,
   'data' : ['activity_data.xml',
             'ir.model.access.csv',
      'activity_seqence.xml',
      'activity_view.xml',
             'reports/report.xml',
             'reports/reciept.xml',
             ],
   'depends': ['hotel_reservation','base','hotel']
}


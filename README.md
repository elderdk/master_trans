# todos


5. Add more supported file types
    A. At least .docx and .xlsx must be supported.

7. Enable tag recognition and editing

9. add google / papago nmt (initially with my api but give users option to add their own. mine = default for now)

10. make a project report page. after creating a new project, user should be directed to here.
    In the report, information included should be: pj name, creator name, client name, fuzzy match, total word count

11. Filter function
    filter by: status, source text, target text, user who translated (or other actions) it

12. Add option to display ALL segments of the file in one page

13. Add javascript onchange action so 'Not transalted' status will change to 'draft' once the user types something in

14. commit at the last segment to move to the next page

15. add celery function so project creation so the user won't have to wait while segmentizing a long file is taking place.

16. add google allauth
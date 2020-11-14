# todos


3. Segment navigation
    A. When committing a segment, the cursor should go to the last non-committed
        segment, i.e. it should skip all comitted segments

4. Segment pagination
    
    B. There should be a default seg num for each page but should be configurable
        right in the segment list view.
    C. Allow user to type in a segment and automatically move to the page that contains the segment
    D. Allow user to type in a page number and automatically move to that page

5. Add more supported file types
    A. At least .docx and .xlsx must be supported.

7. Enable tag recognition and editing

8. When a client is not assigned during the project creation, automatically
    create a client with the same name as the user who created the project

9. Creator of the project should be assigned all of the roles

10. When creating a new project, each segment should have a foreignkey to a model called Distance,
    wherein the segment (or many) within the database with the shortest distance, is created
    This is to take the burden of finding the shortest distance segment and place it to the beginning of the process.
    To be able to better handle large files, Celery should be implemented from the start.

11. Add google nmt below diffview

12. If no client is determined, the client should be the user

13. Include ." exclusion in the exclusion regex
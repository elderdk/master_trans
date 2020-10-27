# todos

1. Add sentence break exclusions
    sentences should not break at the end of certain patterns
    e.g.
        Mr. Elder was walking down the street.

    When segmentized now:
        1. Mr.
        2. Elder was walking down the street.

    This should not happen.

2. Workers role distinction
    A. when (or after) creating a project, the creator or a staff member
        should be able to assign workers and determine their roles
        e.g.
            File 1: 
                Mr. A - translator
                Mr. B - reviewer
                Mr. C - QA
                Mr. D - T/O
                Creator - sign-off
    
    B. When opening a file, each worker should only be able to open the file
        in the mode that they are assigned to.
        e.g.
            Mr. A (translator) can only work on the file to translate.
            This means that when Mr. A commits a segment, the status will only
            change to "Translated"
            If Mr. B (reviewr) accesses the file as a reviewer, any edit he makes
            should change the seg status as "translation rejected" and
            any commit should change the status to "translation accepted"
    
    C. Each file should display the work mode (T or R) available to that user 
        (nothing if no role is assigned)

3. Segment navigation
    A. When committing a segment, the cursor should go to the last non-committed
        segment, i.e. it should skip all comitted segments

4. Segment pagination
    A. add segment pagination.
    B. There should be a default seg num for each page but should be configurable
        right in the segment list view.

5. Add more supported file types
    A. At least .docx and .xlsx must be supported.

6. Enable target generation
    A. Once translation is completed, a button should be available to
        generate the target file with all the linebreaks and PR breaks
        implemented as exactly as the original file. (including all tax formatting)

7. Enable tag recognition and editing

8. When a client is not assigned during the project creation, automatically
    create a client with the same name as the user who created the project
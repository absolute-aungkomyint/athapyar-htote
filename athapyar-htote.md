# AthaPyar Htote   
   
# {{AthaPyar Htote}} — Proposal by @{{absolute-aungkomyint}}   
### Gist   
- Personal Budget Management Software   
   
   
### Story   
- People keep losing traces of their financial progress.   
-  Hate Spreadsheets.    
- Another Variant for Financial Management.   
- Fast and low weight.   
-  Easy interface rather than massive tables and column views.   
- Run on local device with no-internet.   
   
   
### Why   
- It empowers users to take control of their finances without the overhead of complex accounting software.   
- Financial clarity improves as tracking becomes a frictionless habit rather than a chore.   
- It removes the "spreadsheet fatigue" and the anxiety of data privacy by keeping everything offline and local.   
   
   
### Why Not   
- We are not building a multi-user collaborative platform or a cloud-synced service.   
- We are not building a full-fledged accounting suite with tax filing or business payroll features.   
   
   
### Tech Spec   
- Built as a local-first desktop or mobile application.   
- **Stack:** Python with SQLite for local storage and the Rich library for the terminal-based UI.   
- **Main Pieces:** A fast transaction logger, a category-based budget tracker, and simple visualization charts for monthly spending.   
   
   
### Definition of Done   
- [ ] Core local database schema implemented.   
- [ ] Transaction entry interface functional and "fast".   
- [ ] Monthly budget overview visualization complete.   
- [ ] Offline-first capability verified (no internet required).   

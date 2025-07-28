# Log-Anomaly
As per the flowchart discussed with ma'am, and whose picture is up on the group
Uses the Loghub/Apache Server log dataset
Done so far:
 - Preprocessed dataset: Logs classified into different events; documentation at https://docs.google.com/document/d/12PeiPaygQXKVjj3eWI5UZ43nSOdPuVI6G8jFmEKHdT8/edit?usp=sharing
 - Made windows of size 3 and also based on time

To do (in the next 2 days, commit regularly so that we are all on the same page)

Step 1:  Labelling dataset (we will try rule based and unsupervised approaches):
    - Rule based:  E10, E11, and E12 are anomalies encountered during boot of the server. Sequences containing these events can be classified as anomalous. Not perfect, but we can start with this.
    - Unsupervised: Lets make a Jupyter notebook that tests out  5 unsupervised strategies to label anomalous sequences- DBSCAN, Isolation Forests, Local Outlier Factor, Elliptic Envelope, One-Class         Support Vector Machines as detailed in this article- https://medium.com/learningdatascience/anomaly-detection-techniques-in-python-50f650c75aaf

Step 2: Supervised learnig methods for anomaly detection:
    - For the demonstration, let us try 4 methods: Logistic Regression, C-Support Vector Classification (because it is good for high dimensional vector spaces) and one Ensemble Method (RF, XGBoost). We can try neural nets and other deep learning techniques for the next demonstration.

Step 3: Presentation to explain to our mentors what our progress has been so far (not a lot, but still lol)
    Link: https://docs.google.com/presentation/d/1BVV2lfPSrt31vgrG9gZTrPHSLwYKssGIv281wgXq0ew/edit?usp=sharing (Given access to y'alls' RVCE mails)
  - Shows accuracy, ROC curves, trainign curves, clustering diagrams (whatever is relevant)
  - Sources and references


My references and inspirations:
1. https://ieee-dataport.org/open-access/apache-web-server-access-log-pre-processing-web-intrusion-detection
2. https://jiemingzhu.github.io/pub/pjhe_icws2017.pdf
3. https://medium.com/@enyel.salas84/intro-to-log-analysis-958e28673f51
4. https://arxiv.org/pdf/2107.05908
5. GOAT reference: https://view.officeapps.live.com/op/view.aspx?src=https%3A%2F%2Fnetman.aiops.org%2F~peidan%2FANM2022%2F6.LogAnomalyDetection%2FLectureCoverage%2F2016ISSRE_System%2520Log%2520Analysis%2520for%2520Anomaly%2520Detection.pptx&wdOrigin=BROWSELINK
6. https://builtin.com/machine-learning/nlp-word2vec-python


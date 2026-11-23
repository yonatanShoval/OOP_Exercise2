You are reviewing two student submissions for the same university assignment. Each attached file is one repository, packed into text: first the full file tree with sizes, then the text files, most important first. Files listed under "Not included" at the end of a bundle were left out only because of size. Do not treat them as missing, and do not guess their content.

Call the submissions only "Repo A" and "Repo B". Do not mention any person's name.

Review each submission mainly as text: the README and the documentation. Check whether they address the requirements, the algorithm, and how to run the project. Look at the code only to check what the documents claim. This review supports a human grader and does not replace one.

The assignment (Ex1, Introduction to Software Engineering):
- Task: project a 3D volume (NRRD file, values of 8, 16 or 32 bits, each side from 1 to 1023) onto a plane, and return a 2D image.
- The plane is given by 3 points (an isosceles triangle, |dist(a,b) - dist(a,c)| < 0.001) or by 4 points (an isosceles trapezoid).
- The assignment gives a step-by-step projection algorithm. Points outside the volume give 0. The closest voxel is enough.
- The focus is on the design and the general quality of the code, more than on the algorithm.
- Speed: for a 500^3 volume, at least 100 fps is expected, and 30 fps is a must.
- Language: Java, Python, C or C++. The code must be correct and stable.
- To-do list:
  1. A README with the problem and the scope.
  2. An SRS.
  3. The main algorithm, defined in detail.
  4. A data set of NRRD files.
  5. A testing strategy that also covers the demo.
  6. The implementation, with frequent commits.
  7. A demo run as `python Ex0.py file.nrrd file.csv file.mp4`. The CSV holds a list of 3 or 4 point coordinates, and the MP4 has one frame per plane, in order.
  8. An experiment, with a short description of the results and the MP4 output.
- Invalid input: an invalid point set raises an exception. In the demo, it becomes an "error frame" (for example a black frame with a mark), and the valid planes still give correct frames.
- Submission: a public GitHub repository with all the docs, the code, how to build and run it, and links to supplementary materials (benchmarks, videos).

Please answer in English, in this order:

1. For each repo, a table with one row per to-do item and per requirement above. Columns: Status (done / partly / missing / not visible in the bundle) and Evidence (the file name, in one short line).
2. For each repo: three strengths and three weaknesses of the documentation (does it cover the requirements, the algorithm, and how to run?), each with a file name.
3. A comparison of the two repos: the README, the requirements (SRS), the algorithm description, how to run, testing, and the experiment.
4. A ranking: which repo is documented better, with a short reason for each point.
5. What each repo could learn from the other: up to three points each.

Keep the whole answer under 900 words. If something cannot be checked from the bundle (for example, the real fps), say so instead of guessing.

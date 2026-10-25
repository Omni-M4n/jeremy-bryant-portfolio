# Guided case: review after your first attempt

The first `note.txt` contains six UTF-8 bytes: Hello and one newline. It
meets the rules and gets 201. The app saves it under a new `.txt` name.
The runner resolves the path and checks its parent. It must be the temporary
root folder. The runner also reads the file to check that its bytes match.

The second name is `../note.txt`. Its slashes break the name rule. The app
returns 422 before it writes a file. The third ordinary name gets 201 and
another new storage name. Normal uploads still work after a rejection.

The expected statuses are 201, 422, 201. For accepted files, the evidence
should show that the path stayed inside the folder and the content matched.
It should show neither result for the rejected request.
`temporary_uploads_removed` confirms that the runner removed its own sample
folder. The saved receipt is still there for review.

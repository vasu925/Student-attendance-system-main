-- Apply once to the existing MySQL database before deploying this version.
-- Back up the database first. Existing student records remain untouched.
-- Faculty must issue a fresh code to each authorized student from the Students page.
ALTER TABLE student ADD COLUMN access_code_hash VARCHAR(255) NULL;

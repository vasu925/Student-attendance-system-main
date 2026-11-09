-- Apply once to the existing MySQL database before deploying this version.
-- Back up the database first. Existing students must have DOB populated by authorized staff.
ALTER TABLE student
  ADD COLUMN date_of_birth DATE NULL,
  ADD COLUMN password_hash VARCHAR(255) NULL;

-- After this migration, edit each student record and enter their verified date of birth.
-- Students activate their account on first login and choose their own password.

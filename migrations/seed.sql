-- Seed data for System Settings
INSERT INTO system_settings (key, value) VALUES
('ai_global_enabled', 'true')
ON CONFLICT (key) DO NOTHING;

-- Seed data for Knowledge Base
INSERT INTO knowledge_categories (name, slug, description, icon, order_index) VALUES
('Grammar', 'grammar', 'English grammar rules by level', 'book', 1),
('Vocabulary', 'vocabulary', 'Thematic word lists', 'list', 2),
('Exam Tips', 'exam-tips', 'Preparation tips for exams', 'target', 3);

INSERT INTO knowledge_docs (category_id, title, slug, file_path, cefr_level, description) VALUES
(1, 'A1 Basic Grammar', 'a1-basic-grammar', 'grammar/A1_basic.md', 'A1', 'Fundamental grammar for beginners'),
(1, 'A2 Elementary Grammar', 'a2-elementary-grammar', 'grammar/A2_basic.md', 'A2', 'Elementary grammar structures'),
(1, 'B1 Intermediate Grammar', 'b1-intermediate-grammar', 'grammar/B1_basic.md', 'B1', 'Intermediate grammar rules'),
(1, 'B2 Upper-Intermediate Grammar', 'b2-upper-intermediate-grammar', 'grammar/B2_basic.md', 'B2', 'Upper-intermediate grammar'),
(1, 'C1 Advanced Grammar', 'c1-advanced-grammar', 'grammar/C1_basic.md', 'C1', 'Advanced grammar concepts'),
(1, 'C2 Mastery Grammar', 'c2-mastery-grammar', 'grammar/C2_mastery.md', 'C2', 'Master-level grammar'),
(2, 'A1 Basic Vocabulary', 'a1-basic-vocabulary', 'vocabulary/A1_words.md', 'A1', 'Essential everyday words'),
(2, 'A2 Elementary Vocabulary', 'a2-elementary-vocabulary', 'vocabulary/A2_words.md', 'A2', 'Expanding basic vocabulary'),
(3, 'CEFR Overview', 'cefr-overview', 'exam_tips/cefr_overview.md', NULL, 'Guide to CEFR levels'),
(3, 'IELTS Tips', 'ielts-tips', 'exam_tips/ielts_tips.md', NULL, 'IELTS exam preparation tips'),
(3, 'TOEFL Tips', 'toefl-tips', 'exam_tips/toefl_tips.md', NULL, 'TOEFL exam preparation tips');
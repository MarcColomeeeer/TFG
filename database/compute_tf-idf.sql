insert into doc_freq (word_id, df)
select word_id, count(distinct paper_id)
from paper_word 
group by word_id;


INSERT INTO paper_word_reduced (paper_id, word_id, count, tf_idf)
SELECT pw.paper_id, pw.word_id, pw.count, pw.tf_idf
FROM paper_word pw
JOIN doc_freq df ON pw.word_id = df.word_id
WHERE df.df > 10 AND df.df < 100000;

   
WITH total_papers AS (
    SELECT COUNT(*) AS N FROM paper
)
UPDATE paper_word_reduced pw
SET tf_idf = pw.count * LOG(tp.N * 1.0 / df.df)
FROM doc_freq df, total_papers tp
WHERE pw.word_id = df.word_id;
    
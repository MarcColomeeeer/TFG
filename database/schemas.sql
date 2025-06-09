create table category (
  id VARCHAR primary key,
  name VARCHAR
);

create table subcategory (
  id VARCHAR primary key,
  name VARCHAR,
  category VARCHAR not null,
  foreign key (category) references category(ID)
);

create table paper (
  id VARCHAR primary key,
  title VARCHAR,
  published_year INTEGER,
  summary TEXT,
  dim1 FLOAT,
  dim2 FLOAT,
  subcategory VARCHAR not null,
  foreign key (subcategory) references subcategory(ID)
);

create table author (
  id INTEGER primary key,
  name VARCHAR
);

create table word (
  id INTEGER primary key,
  word VARCHAR
);

create table paper_author (
  paper_id VARCHAR,
  author_id INTEGER,
  primary key (paper_id, author_id),
  foreign key (paper_id) references paper(ID),
  foreign key (author_id) references author(ID)
);

create table paper_word (
  paper_id VARCHAR,
  word_id INTEGER,
  tf_idf FLOAT,
  primary key (paper_id, word_id),
  foreign key (paper_id) references paper(id),
  foreign key (word_id) references word(id)
);

create TABLE document_frequency(
	word_id INTEGER primary key,
	df INTEGER,
	foreign key (word_id) references word(id)
);
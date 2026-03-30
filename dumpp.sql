--
-- PostgreSQL database dump
--

\restrict g4TgDIZ7QcWG52cFZxeFa5agUsToCp3E1XeGIjYf6uIRgcsGZsXBuDQaQ9edKAp

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: coffee_machines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.coffee_machines (
    id integer NOT NULL,
    model character varying(100) NOT NULL,
    barcode character varying(100) NOT NULL,
    rent_price double precision NOT NULL,
    tenant character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    deposit double precision NOT NULL,
    start_date date NOT NULL,
    "in_1C" boolean,
    status character varying(20),
    buyout boolean,
    buyout_date date,
    payments date[],
    deal_type character varying(20),
    comment text,
    full_price double precision
);


--
-- Name: coffee_machines_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.coffee_machines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: coffee_machines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.coffee_machines_id_seq OWNED BY public.coffee_machines.id;


--
-- Name: machine_models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.machine_models (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    default_rent double precision NOT NULL,
    full_price double precision NOT NULL
);


--
-- Name: machine_models_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.machine_models_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: machine_models_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.machine_models_id_seq OWNED BY public.machine_models.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    machine_id integer,
    tenant character varying(100) NOT NULL,
    amount double precision NOT NULL,
    payment_date date NOT NULL,
    is_deposit boolean,
    is_buyout boolean
);


--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: coffee_machines id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coffee_machines ALTER COLUMN id SET DEFAULT nextval('public.coffee_machines_id_seq'::regclass);


--
-- Name: machine_models id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_models ALTER COLUMN id SET DEFAULT nextval('public.machine_models_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Data for Name: coffee_machines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.coffee_machines (id, model, barcode, rent_price, tenant, phone, deposit, start_date, "in_1C", status, buyout, buyout_date, payments, deal_type, comment, full_price) FROM stdin;
17	SES 920+молка	0035	8000	Муралиева Зухра	996556545333	10000	2025-09-11	f	active	f	\N	{}	Аренда	\N	\N
19	SES880	uzdCq	5000	Жумабеков Эсен.	996701405002	10000	2025-09-17	f	active	f	\N	{}	Аренда	\N	\N
20	SES 990	A1SGAESA210200321	10000	Чолпон Муратбекова	996555020817	15000	2025-09-28	f	active	f	\N	{}	Аренда	\N	\N
2	BES875	0781	5000	Сатаров Чынгыз	996755281311	10000	2025-07-09	f	buyout	t	2025-10-03	{}	Рассрочка	Если заранее закроется скидка 1000	\N
3	SES 990	????	10000	Кафе DROVA	996555190650	15000	2025-07-15	f	buyout	t	2025-10-03	{}	Аренда	\N	\N
4	SES 990	0389	10000	БАХТИЯР НУРЛАНОВ	996705885888	10000	2025-07-18	f	buyout	t	2025-10-03	{}	Аренда	\N	\N
5	SES880	0	5000	Шоболот ик	996000000000	10000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
6	SES880	A1SGAESA212405748	5000	БАХТИЯР НУРЛАНОВ	996000000000	10000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
7	SES 990	A1SGAESA213606436	20000	КАЙНАР	996000000000	20000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
8	SES 990	ASGAESA212700607	10000	ПЕГАС.Жаштаева Айгуль	996000000000	0	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
9	Ses878	A1SGAESA211303135	5000	САРЫГУЛОВ ДАЙЫРБЕК	996000000000	10000	2025-08-18	t	buyout	t	2025-10-03	{}	Рассрочка	\N	\N
10	Ses880*3	A1SGAESA205001794	15000	Касымова Айзада. Поезд	996000000000	5000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
11	SES 990	A1SGASA212406673	10000	Ахмади Эркер.	996000000000	15000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
12	SES 990	220	10000	Амина Жартаева	996000000000	5000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
13	Ses980	_0557	9000	Султанова Гулчакы	996000000000	15000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
14	SES 990	226	10000	Абдулаева Саида	996000000000	15000	2025-08-18	t	buyout	t	2025-10-03	{}	Аренда	\N	\N
15	SES880	8505	5000	Асанбеков Шабдан	996709777900	10000	2025-08-20	f	buyout	t	2025-10-03	{}	Аренда	\N	\N
21	Ses878	——	5000	Ташматова Сайкал	996705252519	10000	2025-09-28	f	buyout	t	2025-10-03	{}	Аренда	\N	\N
27	Ses980	A1SGAESA202800557	9000	Азат Садыгалиев.	996555020817	6000	2025-10-03	f	buyout	t	2025-10-03	{}	Аренда	\N	\N
30	Ses980	A1SGAESA202800557*	9000	Азат Садыгалиев	996555020817	6000	2025-10-03	f	buyout	t	2025-10-03	{}	Аренда	Это его вторая кофемашина. Депозит поделен на две кофемашины. Номер телефона 996555020817	\N
24	Ses878	—	5000	Мирлан Абдувалиев	996770316710	10000	2025-09-28	f	active	f	\N	{}	Аренда	\N	50000
16	SES 990	1234	10000	Нышанбу Ж. И.	996552689116	15000	2025-09-02	f	buyout	t	2025-10-03	{}	Аренда	ушел на реалку Зарине ИК	\N
39	SES 990	001200	10000	Атабаев Уран	996504165051	0	2025-10-03	f	active	f	\N	{}	Аренда	Депозит кофемолка	\N
43	SES 990	000801	10000	Исаева Чынар	996500094627	15000	2025-10-27	f	active	f	\N	{}	Аренда	\N	\N
45	SES 990	A1SGFESA224200106 КБ	10000	Канат Бакашаев	996707000440	15000	2025-10-27	f	active	f	\N	{}	Аренда	\N	\N
49	SES 920+молка	001142	8000	Жапарова Анара	996990880302	10000	2025-11-01	f	active	f	\N	{}	Аренда	\N	\N
50	SES 920+молка	001144	8000	Жапарова Анара	996990880302	10000	2025-11-01	f	active	f	\N	{}	Аренда	Вторая кофемашина	\N
51	SES 920+молка	0141 01112025	8000	мураткан Самарбек	996225009777	10000	2025-11-01	f	buyout	t	2025-10-12	{}	Аренда	\N	\N
1	SES880	7783	5000	Рыскулова Керемет	996997502503	10000	2025-07-09	f	buyout	t	2025-08-30	{}	Рассрочка	\N	\N
52	SES 920+молка	001458	8000	Нурзада Нурмуханбетова	996503960022	5000	2025-11-30	f	active	f	\N	{}	Аренда	\N	\N
44	SES880	A1SGAESA220802661 АГ	5000	Абыщова Гульзат	996706605091	10000	2025-10-27	f	buyout	t	2025-11-22	{}	Аренда	\N	\N
47	SES 990	0389 011125	10000	Кюнтуу Улуу Байэль	996704736374	15000	2025-11-01	f	returned	f	\N	{}	Аренда	\N	\N
42	SES 980	001608	9000	Алимжонова Зарина	996554197779	30000	2025-10-13	f	returned	f	\N	{}	Аренда	Штрих в договоре	\N
40	SES 990	0226	10000	Ламзаров Арли	996708088880	15000	2025-10-10	f	buyout	t	2025-11-22	{}	Аренда	\N	\N
41	SES880	.	5000	Сардарбек Худайбердиев	996707777998	10000	2025-10-10	f	buyout	t	2025-11-22	{}	Аренда	Штрих в договоре	\N
18	SES 990	0106	10000	Камиля Арапбаева	996999980888	15000	2025-09-15	f	buyout	t	2025-10-05	{}	Аренда	\N	\N
31	SES 980	A1SGAESA202800557**	9000	Азат Садыгалиев	996555020817	6000	2025-10-03	f	buyout	t	2025-10-02	{}	Аренда	\N	\N
33	SES 878	—-	5000	Ташматова Сайкал	996705252519	10000	2025-10-03	f	buyout	t	2025-10-02	{}	Аренда	\N	\N
22	SES 920+молка	2981, A1SGACGA212300084	8000	Милана Муратбекова	996500023000	15000	2025-09-28	f	buyout	t	2025-10-02	{}	Аренда	\N	\N
35	SES 990	0001	10000	Джумалиев Нурдин	996998755094	15000	2025-10-03	f	buyout	t	2025-10-02	{}	Аренда	\N	\N
38	SES 878	A1SG	5000	Мустапакулов Сактанбек	996555940906	10000	2025-10-03	f	returned	f	\N	{}	Аренда	штрих код полный A1SGAESA211303135	\N
53	BES875	001501	5000	Талайбек Улу Талантбек	996500411445	10000	2025-11-30	f	active	f	\N	{}	Аренда	\N	\N
54	BES920	A1SGAESA222400003 ; A214800139 ;A1SGAESA200600057	21000	Ибрагим Пазилов	996703232271	20000	2025-11-30	f	active	f	\N	{}	Аренда	(только кофемашина без комплекта.)	\N
55	SES 990	A1SGAESA214606694|3011	10000	Антон Кичуткин	996557655777	15000	2025-11-30	f	active	f	\N	{}	Аренда	(рассрочка планирует.)	\N
56	SES 990	A1SGAESA214807171	10000	Айбек Сапаков	996507686686	0	2025-11-30	f	active	f	\N	{}	Аренда	\N	\N
57	SES 920+молка	A210900139, A1SGACGA220200456	8000	Нина Макарова	996702149136	35950	2025-11-30	f	active	f	\N	{}	Аренда	\N	\N
58	SES 990	0422,	10000	Чутбаева Нургуль	996770800055	17000	2025-11-30	f	active	f	\N	{}	Аренда	кофемаш. 105000; чайник 11000	\N
59	SES 980	0049,	9000	Айжамал Махмедова	996709092192	15000	2025-11-30	f	active	f	\N	{}	Аренда	Комплект: \nПитчер 550, 100, 100\nТемпер. Мусорка, таблетки.	\N
60	SES 990	0453	10000	Аширов Дастан.	996554152224	15000	2025-11-30	f	active	f	\N	{}	Аренда	\N	\N
61	BES875	A1SGAESA215003066	4000	Богданов Виктор	996554144189	0	2025-11-30	f	active	f	\N	{}	Аренда	ВИТЯ. ДИЛЛЕР.	\N
62	SES 920+молка	RM1906 ; 1769	8000	Женишбек Жаныбеков	996558808260	15000	2025-12-05	f	active	f	\N	{}	Аренда	Мусорка, темперx2, питчер 550, 100, 100. Весы.	\N
63	SES 990	4769	10000	Заирова Шерингуль	996557250677	15000	2025-12-05	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 550, 100, 100.	\N
64	SES 990	0327|05.12	10000	Тихомирова Татьяна	996555555085	15000	2025-12-05	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 550, 100, 100.	\N
65	SES 990	0060|05.12	10000	Бектур Эмилисов	996700747277	15000	2025-12-05	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 550, 100, 100.	\N
66	SES 980	0227|05/12	9000	Байназаров Калычбек	996709795585	0	2025-12-05	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 550, 100, 100.Весы. Залог паспорт	\N
48	SES880	001140	5000	Каримов Ансар	996507252555	10000	2025-11-01	f	returned	f	\N	{}	Аренда	Штрих в договоре	\N
32	SES 980	996555020817***	9000	Азат Садыгалиев	996555020817	6000	2025-10-03	f	buyout	t	2025-10-02	{}	Аренда	Это его вторая кофемашина. Депозит поделен на две кофемашины. Номер телефона 996555020817	\N
67	SES 878	—06.12	5000	Беков Сыймык	996888101001	3000	2025-12-06	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 350. Старые клиенты, опять взяли.	\N
68	SES 878	—\\06.12	5000	Токторбаев Жаныш	996501901573	5000	2025-12-06	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер 350. Старые клиенты, опять взяли.	\N
69	SES 990	1648.0101	10000	Орозбаев Иса	996707554449	15000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
70	SES 990	16530101	10000	Арзыматов Жанарбек	996554697788	5000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
71	SES 990	16550101	10000	Ринат Курманбеков	996705889904	10000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
72	SES 990	Лезет Айнура Абдуваситова	10000	Лезет Айнура Абдуваситова	996700088261	15000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
74	SES 990	17010101	10000	КРСУ	996550545094	15000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550 таблетки	\N
75	BES920	17030101	8000	Дуйшова Кудайберди	996700430331	10000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
76	SES 878	A1SKFESA211800536	5000	Мукашев Ильдар	996508889333	5000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
77	SES 920+молка	17100101	8000	Аяна Талдыбекова	996708337320	4000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
78	SES 990	17110101	10000	Альмира Пансионат Асылташ	996555078371	3250	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
79	SES 990	17130101	10000	Альмира Пансионат Асылташ	996555078371	3250	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, темпер, питчер550, 100,100, таблетки	\N
80	SES880	17150101	5000	Салон Байтик тару	996700300045	4000	2026-01-01	f	active	f	\N	{}	Аренда	Питчеры 350 и коврик, мусорка	\N
81	BES875	17160101	5000	Улан Шаминалиев	996995754875	15000	2026-01-01	f	active	f	\N	{}	Аренда	Питчеры 350, мусорка, кофе 250	\N
82	SES 878	3135/1218	5000	Мария кателина. Барбершоп	996552215910	10000	2026-01-01	f	active	f	\N	{}	Аренда	Питчеры 350, мусорка, коврик, кольцо	\N
83	BES875	2482/1720	5000	Кумакеев Артур	996559911990	5000	2026-01-01	f	active	f	\N	{}	Аренда	Питчеры 350, мусорка, коврик, кольцо, кофе 250	\N
84	SES 990	Жакшылык Кулбачаев. Арча Бешик	10000	Жакшылык Кулбачаев. Арча Бешик	996700118439	14000	2026-01-01	f	active	f	\N	{}	Аренда	Доставка 1000, Питчеры 550, 100, 100, кофе 1 кг(подарок)	\N
85	SES 980	0227/700122	9000	Зарина Ниязова	996990977997	15000	2026-01-01	f	active	f	\N	{}	Аренда	Мусорка, питчер550, 100,100,	\N
87	SES 990	17260101	10000	Мамытова Аида	996505102777	6000	2026-01-01	f	active	f	\N	{}	Аренда	Питчеры 550, 100, 100	\N
\.


--
-- Data for Name: machine_models; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.machine_models (id, name, default_rent, full_price) FROM stdin;
2	SES880	5000	55000
4	SES 990	10000	110000
5	BES920	8000	85000
6	BES875	5000	34000
8	Ses880*3	15000	5000
10	SES 920+молка	8000	85000
12	SES 878	5000	50000
13	SES 980	9000	95000
14	SES 876	5000	40000
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payments (id, machine_id, tenant, amount, payment_date, is_deposit, is_buyout) FROM stdin;
2	2	Сатаров Чынгыз	5000	2025-07-07	f	f
3	1	Рыскулова Керемет	5000	2025-09-07	f	f
4	15	Асанбеков Шабдан	5000	2025-08-10	f	f
5	16	Нышанбу Ж. И.	10000	2025-08-30	f	f
6	17	Муралиева Зухра	8000	2025-09-10	f	f
7	18	Камиля Арапбаева	10000	2025-09-12	f	f
8	19	Жумабеков Эсен.	5000	2025-09-10	f	f
9	20	Чолпон Муратбекова	10000	2025-09-25	f	f
10	21	Ташматова Сайкал	5000	2025-09-19	f	f
11	22	Милана Муратбекова	8000	2025-09-28	f	f
12	24	Мирлан Абдувалиев	5000	2025-09-19	f	f
13	2	Сатаров Чынгыз	29000	2025-10-03	f	t
26	15	Асанбеков Шабдан	50000	2025-10-03	f	t
27	21	Ташматова Сайкал	0	2025-10-03	f	t
28	27	Азат Садыгалиев.	9000	2025-09-25	f	f
29	27	Азат Садыгалиев.	6000	2025-10-03	f	t
30	30	Азат Садыгалиев	15000	2025-10-03	f	t
31	31	Азат Садыгалиев	9000	2025-09-25	f	f
32	32	Азат Садыгалиев	9000	2025-09-25	f	f
33	33	Ташматова Сайкал	5000	2025-09-19	f	f
34	35	Джумалиев Нурдин	10000	2025-09-26	f	f
35	16	Нышанбу Ж. И.	0	2025-10-03	f	t
36	38	Мустапакулов Сактанбек	5000	2025-10-03	f	f
37	39	Атабаев Уран	10000	2025-09-03	f	f
38	17	Муралиева Зухра	8000	2025-10-09	f	f
39	41	Сардарбек Худайбердиев	5000	2025-10-09	f	f
40	40	Ламзаров Арли	10000	2025-10-07	f	f
41	42	Алимжонова Зарина	9000	2025-10-11	f	f
42	43	Исаева Чынар	10000	2025-10-15	f	f
43	44	Абыщова Гульзат	5000	2025-10-15	f	f
44	45	Канат Бакашаев	10000	2025-10-22	f	f
45	47	Кюнтуу Улуу Байэль	10000	2025-10-13	f	f
46	48	Каримов Ансар	5000	2025-10-15	f	f
47	49	Жапарова Анара	8000	2025-10-26	f	f
48	50	Жапарова Анара	8000	2025-10-26	f	f
49	51	мураткан Самарбек	8000	2025-09-11	f	f
50	51	мураткан Самарбек	77000	2025-10-12	f	t
51	1	Рыскулова Керемет	0	2025-08-30	f	t
52	52	Нурзада Нурмуханбетова	8000	2025-10-27	f	f
53	53	Талайбек Улу Талантбек	5000	2025-10-09	f	f
54	54	Ибрагим Пазилов	21000	2025-11-09	f	f
55	55	Антон Кичуткин	10000	2025-11-11	f	f
56	56	Айбек Сапаков	10000	2025-11-11	f	f
57	57	Нина Макарова	8000	2025-11-13	f	f
58	58	Чутбаева Нургуль	10000	2025-11-17	f	f
59	59	Айжамал Махмедова	9000	2025-11-21	f	f
60	60	Аширов Дастан.	10000	2025-11-19	f	f
61	61	Богданов Виктор	4000	2025-11-19	f	f
62	62	Женишбек Жаныбеков	8000	2025-11-25	f	f
63	63	Заирова Шерингуль	10000	2025-11-26	f	f
64	64	Тихомирова Татьяна	10000	2025-11-26	f	f
65	65	Бектур Эмилисов	10000	2025-12-01	f	f
66	66	Байназаров Калычбек	9000	2025-11-03	f	f
67	44	Абыщова Гульзат	50000	2025-11-22	f	t
68	40	Ламзаров Арли	100000	2025-11-22	f	t
69	41	Сардарбек Худайбердиев	50000	2025-11-22	f	t
70	18	Камиля Арапбаева	100000	2025-10-05	f	t
71	31	Азат Садыгалиев	86000	2025-10-02	f	t
72	32	Азат Садыгалиев	86000	2025-10-02	f	t
73	33	Ташматова Сайкал	45000	2025-10-02	f	t
74	22	Милана Муратбекова	77000	2025-10-02	f	t
75	35	Джумалиев Нурдин	100000	2025-10-02	f	t
76	67	Беков Сыймык	5000	2025-11-22	f	f
77	68	Токторбаев Жаныш	5000	2025-11-26	f	f
78	87	Мамытова Аида	10000	2025-12-31	f	f
79	85	Зарина Ниязова	9000	2025-12-30	f	f
80	84	Жакшылык Кулбачаев. Арча Бешик	10000	2025-12-27	f	f
81	83	Кумакеев Артур	5000	2025-12-27	f	f
82	82	Мария кателина. Барбершоп	5000	2025-12-26	f	f
83	81	Улан Шаминалиев	5000	2025-12-24	f	f
84	80	Салон Байтик тару	5000	2025-12-22	f	f
85	79	Альмира Пансионат Асылташ	10000	2025-12-20	f	f
86	78	Альмира Пансионат Асылташ	10000	2025-12-20	f	f
87	77	Аяна Талдыбекова	8000	2025-12-20	f	f
88	76	Мукашев Ильдар	5000	2025-12-18	f	f
89	75	Дуйшова Кудайберди	10000	2025-12-16	t	f
90	74	КРСУ	10000	2025-12-14	f	f
91	72	Лезет Айнура Абдуваситова	10000	2025-12-13	f	f
92	71	Ринат Курманбеков	10000	2025-12-10	f	f
93	70	Арзыматов Жанарбек	10000	2025-12-09	f	f
94	69	Орозбаев Иса	10000	2025-12-09	f	f
\.


--
-- Name: coffee_machines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.coffee_machines_id_seq', 87, true);


--
-- Name: machine_models_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.machine_models_id_seq', 14, true);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payments_id_seq', 94, true);


--
-- Name: coffee_machines coffee_machines_barcode_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coffee_machines
    ADD CONSTRAINT coffee_machines_barcode_key UNIQUE (barcode);


--
-- Name: coffee_machines coffee_machines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.coffee_machines
    ADD CONSTRAINT coffee_machines_pkey PRIMARY KEY (id);


--
-- Name: machine_models machine_models_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_models
    ADD CONSTRAINT machine_models_name_key UNIQUE (name);


--
-- Name: machine_models machine_models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.machine_models
    ADD CONSTRAINT machine_models_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: payments payments_machine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_machine_id_fkey FOREIGN KEY (machine_id) REFERENCES public.coffee_machines(id);


--
-- PostgreSQL database dump complete
--

\unrestrict g4TgDIZ7QcWG52cFZxeFa5agUsToCp3E1XeGIjYf6uIRgcsGZsXBuDQaQ9edKAp


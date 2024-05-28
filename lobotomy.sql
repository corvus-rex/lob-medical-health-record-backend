PGDMP         *                |            lobotomy_medical_record    14.2    14.2 F    b           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            c           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            d           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            e           1262    24576    lobotomy_medical_record    DATABASE     {   CREATE DATABASE lobotomy_medical_record WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'English_United States.1252';
 '   DROP DATABASE lobotomy_medical_record;
                postgres    false            �            1259    24584    admin    TABLE       CREATE TABLE public.admin (
    admin_id uuid NOT NULL,
    user_id uuid NOT NULL,
    name character varying NOT NULL,
    dob date NOT NULL,
    national_id integer NOT NULL,
    tax_number integer NOT NULL,
    phone_num integer,
    address character varying,
    sex boolean
);
    DROP TABLE public.admin;
       public         heap    postgres    false            �            1259    24759    clinical_entry    TABLE     c  CREATE TABLE public.clinical_entry (
    entry_id uuid NOT NULL,
    record_id uuid NOT NULL,
    entry_date date NOT NULL,
    staff_id uuid NOT NULL,
    height integer,
    weight integer,
    body_temp double precision,
    blood_type character varying(3),
    systolic integer,
    diastolic integer,
    pulse integer,
    note character varying
);
 "   DROP TABLE public.clinical_entry;
       public         heap    postgres    false            �            1259    24618    doctor    TABLE     �  CREATE TABLE public.doctor (
    doctor_id uuid NOT NULL,
    user_id uuid NOT NULL,
    name character varying NOT NULL,
    dob date NOT NULL,
    national_id integer,
    phone_num integer NOT NULL,
    address character varying,
    pob character varying NOT NULL,
    license_num character varying NOT NULL,
    tax_num integer NOT NULL,
    historical jsonb NOT NULL,
    sex boolean
);
    DROP TABLE public.doctor;
       public         heap    postgres    false            �            1259    24671    doctor_poly    TABLE     \   CREATE TABLE public.doctor_poly (
    doctor_id uuid NOT NULL,
    poly_id uuid NOT NULL
);
    DROP TABLE public.doctor_poly;
       public         heap    postgres    false            �            1259    24606 	   insurance    TABLE     q   CREATE TABLE public.insurance (
    insurance_id uuid NOT NULL,
    insurance_name character varying NOT NULL
);
    DROP TABLE public.insurance;
       public         heap    postgres    false            �            1259    24737 
   lab_report    TABLE     �   CREATE TABLE public.lab_report (
    report_id uuid NOT NULL,
    record_id uuid NOT NULL,
    report_date date NOT NULL,
    lab_note character varying NOT NULL,
    staff_id uuid NOT NULL,
    lab_id uuid NOT NULL,
    attachment character varying
);
    DROP TABLE public.lab_report;
       public         heap    postgres    false            �            1259    24642 
   laboratory    TABLE     �   CREATE TABLE public.laboratory (
    lab_id uuid NOT NULL,
    lab_name character varying NOT NULL,
    lab_desc character varying
);
    DROP TABLE public.laboratory;
       public         heap    postgres    false            �            1259    24715    medical_note    TABLE     +  CREATE TABLE public.medical_note (
    note_id uuid NOT NULL,
    record_id uuid NOT NULL,
    note_date date NOT NULL,
    note_content character varying NOT NULL,
    doctor_id uuid NOT NULL,
    poly_id uuid NOT NULL,
    attachment character varying,
    diagnosis character varying NOT NULL
);
     DROP TABLE public.medical_note;
       public         heap    postgres    false            �            1259    24705    medical_record    TABLE     �   CREATE TABLE public.medical_record (
    record_id uuid NOT NULL,
    patient_id uuid NOT NULL,
    created_date time with time zone NOT NULL,
    last_editted time with time zone NOT NULL
);
 "   DROP TABLE public.medical_record;
       public         heap    postgres    false            �            1259    24628    medical_staff    TABLE     �  CREATE TABLE public.medical_staff (
    staff_id uuid NOT NULL,
    user_id uuid NOT NULL,
    name character varying NOT NULL,
    dob date NOT NULL,
    national_id integer,
    phone_num integer NOT NULL,
    address character varying,
    pob character varying NOT NULL,
    license_num character varying NOT NULL,
    tax_num integer NOT NULL,
    historical jsonb NOT NULL,
    sex boolean
);
 !   DROP TABLE public.medical_staff;
       public         heap    postgres    false            �            1259    24596    patient    TABLE     N  CREATE TABLE public.patient (
    patient_id uuid NOT NULL,
    user_id uuid NOT NULL,
    name character varying NOT NULL,
    dob date NOT NULL,
    national_id integer,
    phone_num integer NOT NULL,
    address character varying,
    alias character varying,
    relative_phone integer,
    insurance_id uuid,
    sex boolean
);
    DROP TABLE public.patient;
       public         heap    postgres    false            �            1259    32775    patient_interest    TABLE     �   CREATE TABLE public.patient_interest (
    patient_id uuid NOT NULL,
    doctor_id uuid NOT NULL,
    staff_id uuid NOT NULL
);
 $   DROP TABLE public.patient_interest;
       public         heap    postgres    false            �            1259    24664 
   polyclinic    TABLE     �   CREATE TABLE public.polyclinic (
    poly_id uuid NOT NULL,
    poly_name character varying NOT NULL,
    poly_desc character varying
);
    DROP TABLE public.polyclinic;
       public         heap    postgres    false            �            1259    24649    staff_laboratory    TABLE     _   CREATE TABLE public.staff_laboratory (
    staff_id uuid NOT NULL,
    lab_id uuid NOT NULL
);
 $   DROP TABLE public.staff_laboratory;
       public         heap    postgres    false            �            1259    24577    user    TABLE     �   CREATE TABLE public."user" (
    user_id uuid NOT NULL,
    user_type integer NOT NULL,
    user_name character varying(25) NOT NULL,
    user_email character varying NOT NULL,
    password character varying
);
    DROP TABLE public."user";
       public         heap    postgres    false            R          0    24584    admin 
   TABLE DATA           o   COPY public.admin (admin_id, user_id, name, dob, national_id, tax_number, phone_num, address, sex) FROM stdin;
    public          postgres    false    210   uZ       ^          0    24759    clinical_entry 
   TABLE DATA           �   COPY public.clinical_entry (entry_id, record_id, entry_date, staff_id, height, weight, body_temp, blood_type, systolic, diastolic, pulse, note) FROM stdin;
    public          postgres    false    222   [       U          0    24618    doctor 
   TABLE DATA           �   COPY public.doctor (doctor_id, user_id, name, dob, national_id, phone_num, address, pob, license_num, tax_num, historical, sex) FROM stdin;
    public          postgres    false    213   ![       Z          0    24671    doctor_poly 
   TABLE DATA           9   COPY public.doctor_poly (doctor_id, poly_id) FROM stdin;
    public          postgres    false    218   >[       T          0    24606 	   insurance 
   TABLE DATA           A   COPY public.insurance (insurance_id, insurance_name) FROM stdin;
    public          postgres    false    212   [[       ]          0    24737 
   lab_report 
   TABLE DATA           o   COPY public.lab_report (report_id, record_id, report_date, lab_note, staff_id, lab_id, attachment) FROM stdin;
    public          postgres    false    221   x[       W          0    24642 
   laboratory 
   TABLE DATA           @   COPY public.laboratory (lab_id, lab_name, lab_desc) FROM stdin;
    public          postgres    false    215   �[       \          0    24715    medical_note 
   TABLE DATA           ~   COPY public.medical_note (note_id, record_id, note_date, note_content, doctor_id, poly_id, attachment, diagnosis) FROM stdin;
    public          postgres    false    220   �[       [          0    24705    medical_record 
   TABLE DATA           [   COPY public.medical_record (record_id, patient_id, created_date, last_editted) FROM stdin;
    public          postgres    false    219   �[       V          0    24628    medical_staff 
   TABLE DATA           �   COPY public.medical_staff (staff_id, user_id, name, dob, national_id, phone_num, address, pob, license_num, tax_num, historical, sex) FROM stdin;
    public          postgres    false    214   �[       S          0    24596    patient 
   TABLE DATA           �   COPY public.patient (patient_id, user_id, name, dob, national_id, phone_num, address, alias, relative_phone, insurance_id, sex) FROM stdin;
    public          postgres    false    211   	\       _          0    32775    patient_interest 
   TABLE DATA           K   COPY public.patient_interest (patient_id, doctor_id, staff_id) FROM stdin;
    public          postgres    false    223   &\       Y          0    24664 
   polyclinic 
   TABLE DATA           C   COPY public.polyclinic (poly_id, poly_name, poly_desc) FROM stdin;
    public          postgres    false    217   C\       X          0    24649    staff_laboratory 
   TABLE DATA           <   COPY public.staff_laboratory (staff_id, lab_id) FROM stdin;
    public          postgres    false    216   `\       Q          0    24577    user 
   TABLE DATA           U   COPY public."user" (user_id, user_type, user_name, user_email, password) FROM stdin;
    public          postgres    false    209   }\       �           2606    24590    admin admin_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (admin_id);
 :   ALTER TABLE ONLY public.admin DROP CONSTRAINT admin_pkey;
       public            postgres    false    210            �           2606    24765 "   clinical_entry clinical_entry_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.clinical_entry
    ADD CONSTRAINT clinical_entry_pkey PRIMARY KEY (entry_id);
 L   ALTER TABLE ONLY public.clinical_entry DROP CONSTRAINT clinical_entry_pkey;
       public            postgres    false    222            �           2606    24641    doctor doctor_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT doctor_pkey PRIMARY KEY (doctor_id);
 <   ALTER TABLE ONLY public.doctor DROP CONSTRAINT doctor_pkey;
       public            postgres    false    213            �           2606    24675    doctor_poly doctor_poly_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.doctor_poly
    ADD CONSTRAINT doctor_poly_pkey PRIMARY KEY (doctor_id, poly_id);
 F   ALTER TABLE ONLY public.doctor_poly DROP CONSTRAINT doctor_poly_pkey;
       public            postgres    false    218    218            �           2606    24612    insurance insurances_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.insurance
    ADD CONSTRAINT insurances_pkey PRIMARY KEY (insurance_id);
 C   ALTER TABLE ONLY public.insurance DROP CONSTRAINT insurances_pkey;
       public            postgres    false    212            �           2606    24743    lab_report lab_report_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT lab_report_pkey PRIMARY KEY (report_id);
 D   ALTER TABLE ONLY public.lab_report DROP CONSTRAINT lab_report_pkey;
       public            postgres    false    221            �           2606    24648    laboratory laboratory_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.laboratory
    ADD CONSTRAINT laboratory_pkey PRIMARY KEY (lab_id);
 D   ALTER TABLE ONLY public.laboratory DROP CONSTRAINT laboratory_pkey;
       public            postgres    false    215            �           2606    24721    medical_note medical_note_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.medical_note
    ADD CONSTRAINT medical_note_pkey PRIMARY KEY (note_id);
 H   ALTER TABLE ONLY public.medical_note DROP CONSTRAINT medical_note_pkey;
       public            postgres    false    220            �           2606    24709 "   medical_record medical_record_pkey 
   CONSTRAINT     g   ALTER TABLE ONLY public.medical_record
    ADD CONSTRAINT medical_record_pkey PRIMARY KEY (record_id);
 L   ALTER TABLE ONLY public.medical_record DROP CONSTRAINT medical_record_pkey;
       public            postgres    false    219            �           2606    24634     medical_staff medical_staff_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.medical_staff
    ADD CONSTRAINT medical_staff_pkey PRIMARY KEY (staff_id);
 J   ALTER TABLE ONLY public.medical_staff DROP CONSTRAINT medical_staff_pkey;
       public            postgres    false    214            �           2606    32779 &   patient_interest patient_interest_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.patient_interest
    ADD CONSTRAINT patient_interest_pkey PRIMARY KEY (patient_id);
 P   ALTER TABLE ONLY public.patient_interest DROP CONSTRAINT patient_interest_pkey;
       public            postgres    false    223            �           2606    24692    patient patient_pkey 
   CONSTRAINT     Z   ALTER TABLE ONLY public.patient
    ADD CONSTRAINT patient_pkey PRIMARY KEY (patient_id);
 >   ALTER TABLE ONLY public.patient DROP CONSTRAINT patient_pkey;
       public            postgres    false    211            �           2606    24670    polyclinic polyclinic_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.polyclinic
    ADD CONSTRAINT polyclinic_pkey PRIMARY KEY (poly_id);
 D   ALTER TABLE ONLY public.polyclinic DROP CONSTRAINT polyclinic_pkey;
       public            postgres    false    217            �           2606    24653 &   staff_laboratory staff_laboratory_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.staff_laboratory
    ADD CONSTRAINT staff_laboratory_pkey PRIMARY KEY (staff_id, lab_id);
 P   ALTER TABLE ONLY public.staff_laboratory DROP CONSTRAINT staff_laboratory_pkey;
       public            postgres    false    216    216            �           2606    24583    user user_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public."user" DROP CONSTRAINT user_pkey;
       public            postgres    false    209            �           2606    24676    doctor_poly doctor_id    FK CONSTRAINT     ~   ALTER TABLE ONLY public.doctor_poly
    ADD CONSTRAINT doctor_id FOREIGN KEY (doctor_id) REFERENCES public.doctor(doctor_id);
 ?   ALTER TABLE ONLY public.doctor_poly DROP CONSTRAINT doctor_id;
       public          postgres    false    3228    218    213            �           2606    24722    medical_note doctor_id    FK CONSTRAINT        ALTER TABLE ONLY public.medical_note
    ADD CONSTRAINT doctor_id FOREIGN KEY (doctor_id) REFERENCES public.doctor(doctor_id);
 @   ALTER TABLE ONLY public.medical_note DROP CONSTRAINT doctor_id;
       public          postgres    false    220    3228    213            �           2606    32785    patient_interest doctor_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.patient_interest
    ADD CONSTRAINT doctor_id FOREIGN KEY (doctor_id) REFERENCES public.doctor(doctor_id);
 D   ALTER TABLE ONLY public.patient_interest DROP CONSTRAINT doctor_id;
       public          postgres    false    213    223    3228            �           2606    24613    patient insurance_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.patient
    ADD CONSTRAINT insurance_id FOREIGN KEY (insurance_id) REFERENCES public.insurance(insurance_id) NOT VALID;
 >   ALTER TABLE ONLY public.patient DROP CONSTRAINT insurance_id;
       public          postgres    false    212    211    3226            �           2606    24659    staff_laboratory lab_id    FK CONSTRAINT     ~   ALTER TABLE ONLY public.staff_laboratory
    ADD CONSTRAINT lab_id FOREIGN KEY (lab_id) REFERENCES public.laboratory(lab_id);
 A   ALTER TABLE ONLY public.staff_laboratory DROP CONSTRAINT lab_id;
       public          postgres    false    215    216    3232            �           2606    24754    lab_report lab_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT lab_id FOREIGN KEY (lab_id) REFERENCES public.laboratory(lab_id) NOT VALID;
 ;   ALTER TABLE ONLY public.lab_report DROP CONSTRAINT lab_id;
       public          postgres    false    221    215    3232            �           2606    24710    medical_record patient_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.medical_record
    ADD CONSTRAINT patient_id FOREIGN KEY (patient_id) REFERENCES public.patient(patient_id);
 C   ALTER TABLE ONLY public.medical_record DROP CONSTRAINT patient_id;
       public          postgres    false    3224    219    211            �           2606    32780    patient_interest patient_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.patient_interest
    ADD CONSTRAINT patient_id FOREIGN KEY (patient_id) REFERENCES public.patient(patient_id);
 E   ALTER TABLE ONLY public.patient_interest DROP CONSTRAINT patient_id;
       public          postgres    false    223    211    3224            �           2606    24681    doctor_poly poly_id    FK CONSTRAINT     |   ALTER TABLE ONLY public.doctor_poly
    ADD CONSTRAINT poly_id FOREIGN KEY (poly_id) REFERENCES public.polyclinic(poly_id);
 =   ALTER TABLE ONLY public.doctor_poly DROP CONSTRAINT poly_id;
       public          postgres    false    218    3236    217            �           2606    24727    medical_note poly_id    FK CONSTRAINT     }   ALTER TABLE ONLY public.medical_note
    ADD CONSTRAINT poly_id FOREIGN KEY (poly_id) REFERENCES public.polyclinic(poly_id);
 >   ALTER TABLE ONLY public.medical_note DROP CONSTRAINT poly_id;
       public          postgres    false    220    3236    217            �           2606    24732    medical_note record_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.medical_note
    ADD CONSTRAINT record_id FOREIGN KEY (record_id) REFERENCES public.medical_record(record_id);
 @   ALTER TABLE ONLY public.medical_note DROP CONSTRAINT record_id;
       public          postgres    false    219    3240    220            �           2606    24744    lab_report record_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT record_id FOREIGN KEY (record_id) REFERENCES public.medical_record(record_id) NOT VALID;
 >   ALTER TABLE ONLY public.lab_report DROP CONSTRAINT record_id;
       public          postgres    false    3240    219    221            �           2606    24766    clinical_entry record_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.clinical_entry
    ADD CONSTRAINT record_id FOREIGN KEY (record_id) REFERENCES public.medical_record(record_id);
 B   ALTER TABLE ONLY public.clinical_entry DROP CONSTRAINT record_id;
       public          postgres    false    219    222    3240            �           2606    24654    staff_laboratory staff_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.staff_laboratory
    ADD CONSTRAINT staff_id FOREIGN KEY (staff_id) REFERENCES public.medical_staff(staff_id);
 C   ALTER TABLE ONLY public.staff_laboratory DROP CONSTRAINT staff_id;
       public          postgres    false    214    216    3230            �           2606    24749    lab_report staff_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.lab_report
    ADD CONSTRAINT staff_id FOREIGN KEY (staff_id) REFERENCES public.medical_staff(staff_id) NOT VALID;
 =   ALTER TABLE ONLY public.lab_report DROP CONSTRAINT staff_id;
       public          postgres    false    214    221    3230            �           2606    24771    clinical_entry staff_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.clinical_entry
    ADD CONSTRAINT staff_id FOREIGN KEY (staff_id) REFERENCES public.medical_staff(staff_id);
 A   ALTER TABLE ONLY public.clinical_entry DROP CONSTRAINT staff_id;
       public          postgres    false    214    3230    222            �           2606    32790    patient_interest staff_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.patient_interest
    ADD CONSTRAINT staff_id FOREIGN KEY (staff_id) REFERENCES public.medical_staff(staff_id);
 C   ALTER TABLE ONLY public.patient_interest DROP CONSTRAINT staff_id;
       public          postgres    false    223    3230    214            �           2606    24591    admin user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.admin
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE;
 7   ALTER TABLE ONLY public.admin DROP CONSTRAINT user_id;
       public          postgres    false    210    3220    209            �           2606    24601    patient user_id    FK CONSTRAINT     ~   ALTER TABLE ONLY public.patient
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public."user"(user_id) NOT VALID;
 9   ALTER TABLE ONLY public.patient DROP CONSTRAINT user_id;
       public          postgres    false    211    209    3220            �           2606    24623    doctor user_id    FK CONSTRAINT     }   ALTER TABLE ONLY public.doctor
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public."user"(user_id) NOT VALID;
 8   ALTER TABLE ONLY public.doctor DROP CONSTRAINT user_id;
       public          postgres    false    3220    213    209            �           2606    24635    medical_staff user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.medical_staff
    ADD CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public."user"(user_id) NOT VALID;
 ?   ALTER TABLE ONLY public.medical_staff DROP CONSTRAINT user_id;
       public          postgres    false    209    3220    214            R      x�-˱
1��}��@��-�O7��]�6�¡p��+(?|�o�+�X�[P�� ,�s$NMD��0����ŘA�
4֨��[�1�6}��mj�EN��\��/w��;��K؞���/��<}%J      ^      x������ � �      U      x������ � �      Z      x������ � �      T      x������ � �      ]      x������ � �      W      x������ � �      \      x������ � �      [      x������ � �      V      x������ � �      S      x������ � �      _      x������ � �      Y      x������ � �      X      x������ � �      Q   �   x�EƱ�0 Й~k�T<�fJ��T�4Ѱ\�k�5~��oz����Jz�SQpVqG9p� E�%�o���G�˶���$�6�d:������rZ~̽��{���P��jR^F<����0�J�ن�Ղ1��K+J     
# LightPicture
A python module for creating printable 3d models from raster images.


----------------------
SUMMARY
----------------------
 Image to 3mf file

  The initial goal was to convert a bitmap into a 3D mesh in a fairly specific kind of way
  The resulting 3D mesh must
      - be easy to import into prusa slicer
      - calculate in a reasonable time, considering the amount of potential 'points' in resulting space/mesh
      - easy to programatically customize it's behaviour...
      so that it actually turns into a:

          *-=\_] !!! [_/=-* Programming framework for constructing abstract 3d meshes for printing *-=\_] !!! [_/=-*
          using python and basic concepts like
          - Coordinates
          - Vertex
          - Triangle
          - TriangleMesh
          - and the 3D space itself  
 
    
    
    
    
----------------------
LEGACY: PRELIMINARY SCRAP NOTES
----------------------
   
# v0
Konwersja obrazu do modelu 3D.
Model 3D
- reprezentuje obraz w postaci bryły
- reprezentacja jest z natury monochromatyczna
- bryła, oglądana w płaszczyźnie XY reprezentuje kształt obrazu
- 'odcień' barwy w danym puncie reprezentuje 'grubość' bryły w osi Z

Idea wykonania:
- uzycie formatu 3mf: algorytmiczna generacja opisu bryly w postaci struktury xml

Implementacja:
- python

Zadania:

	[1]. odczyt rastrowego pliku graficznego - pewnei jpg albo bmp - uzyskanie struktury danych reprezentujacych pixele.
	[2]. obliczenie parametrow wierzcholkow i trojkatow opisujacych bryle, reprezentujaca obraz. Utrozenie struktury xml pliku 3mf na podstawie wierzcholkow i trojkatow
		[2.1] Mapowanie ze wspołrzędnych obrazu na współrzędne płaszczyzn XY (rozmiar 'voxela' w plaszczyznie XY)
		[2.2] Mapowanie z jasnosci piksela na grubosc materiału (dynamiczne, byc moze nieliniowe, pewnie zalezne od koloru i rodzaju materialu, specyficzne dla grafiki, etc.)
		[2.3] Budowa struktury wierzchołków opisujących bryłę 
		[2.4] Budowa struktury trójkątów z wierzchołków
				* Miedzy ktorymi wierzcholkami i ile trojkatow zbudowac zeby utworzyc legalną bryłę, jak je wygenerowac algorytmicznie
				* kolejnosc punktow przy definicji trojkata - patrz wymagania 3mf
		[2.5] Uworzenie struktury pliku xlm z wygenerowanych wierzcholkow i trojkatow
	[3]. zapis do pliku 3mf - utworzenie struktury katalogow, zpakowanie do zip, zmiana nazwy na 3mf

TO DO:

	[1]: {DONE}
		Biblioteka PIL daje dostep do plikow graficznych na poziomie pixeli.
		Obsluga wielu formatów, wbudowane funkcje manipulacji obrazem, etc
		
	[2]:
		[2.1]
			polysml:
			1. przeksztalcenie obrazu monochromatycznego o rozmiarach [x,y] pixeli na 2-wymiarowa tablice o rozmiarze [x,y] - niech sei zwie height_array.
			   Wspolrzedne piksela to wspolrzedne tablicy, zas wartosc (liczba dodatnia) to grubosc bryly w osi z w danym miejscu - 
			   inaczej obrazujac: ilosc voxeli o jednostkowym rozmiarze umieszczonych jeden na drugim w formie slupka
			2(a). Na podstawie height_array wyznacznie wierzchołków ograniczających bryłę
			      * w sumie to chyba zwly pomysl poniewaz sciany w plaszczyznach front, left, back, right moga miec ksztalt inny niz prostokat
			        a wtedy i tak potrzebne sa dodatkowe wierzchoki, zeby zbudowac sciane z trojkatow
			2(b). Na podstawie danych z height_array wygenerowac wierzchoki, bedace zewnetrzymi wierzcholkami bryly tak, jakby byla zbudowana z jednostkowych voxeli tzn:
                  Wartosc w height_array[x][y] oznacza ilość jednostkowych voxeli ułożonych na sobie w osi Z.
				  Jak to zrobić?:
					- 8 pierwszych punktów, lezace na plaszczyznie z=0 sa latwe do wyznaczenia: to ksztalt obrazu - 
					  dowolny prostokat w dodatnim kwadrancie układu X,Y o jednym z wierzcholkow w punkcie (0,0,0), bedacy podstawa prostopadloscianu o jdnostkowej wysokości w osi Z.
					  Wszystkie jego sciany oprocz 'top' dzielimy na trojkaty
			2(c). Dla kazdej kombinacji (x,y,z) gdzie x i y to rozmiar obrazu w pixelach a z to najwyzsza z wartosci znajdujacyc sie w height_array (maksymalna wysokosc bryly):
					1. Okresl czy voxel znajduje sie wewnatrz czy na zewnatrz bryly?
					   Jesli na zewnatrz zignoruj i idz do nastepnego.
					2. Czy voxel jest skrajny (czy bylby widoczny)?
					   Jesli nie zignoruj i idz do nastepnego.
					3. Oblicz 8 wierzcholkow danego voxela - conajmniej czesc z nich bedzie niezbedna
					4. 
			
			2(d1)
				  Voxele przy inicjalizacji oblicza pewne atrybuty wlasne na podstawie wspolnej tablicy height_array.
				  Kazdy Voxel zostanie poproszony o wygenerowanie swojej reprezentacji w formie wierzcholkow (globalne x,y,z) 
				    i trojkatow (lokalne odniesienia do 8 wierzcholkow danego voxela) opisujacych jego widoczne sciany.
				  
				  Obiekt klasy LightVoxelBox zawiera kolekcje obiektow LightVoxel i udostepnia dla nich tablice height_array.
				  Ten obiekt wyrenderuje pis 3mf:
					1. wez kazdy z voxeli i wpisz jego punkty na liste, jednoczesnie dajac voxelowi znac jaki numer na liscie ma kazdy jego punktow
					2. popros kazdy voxel o wygenerowanie trojkatow
				  
				  
				  Następnie punkty ze wszsytkich voxeli zostaja zapisane
				  W tym momencie posiadamy informacje o wszystkich wymaganych wierzcholkach i trojkatach rozproszoną we wszystkich voxelach i zawierajaca redundantne wierzcholki.
				  (* problem? - sposob opisu wierzcholkow trojkatow w formacie 3mf - tzn. bezposredni odnosnik do kolejnosci, w ktorej dany wierzcholek zostal zdefiniowany)
				  (* rozwiazanie? - podczas obliczania voxeli, ktore bedzie z natury sekwencyjne, od razu wpisywac wierzcholek na liste i zapamietac jego kolejny numer)
				  
			2(d2)
				  LightVoxel reprezentuje pojedynczy voxel.
				  LightVoxelBox zawiera kolekcje obiektow LightVoxel.
				  
				  LightVoxelBox zawiera 2-wymiarowa tablice height_array, ktora opisuje obraz
				  LightVoxelBox zawiera 3-wymiarowa tablice voxel_space, ktora strukturyzuje LigthtVoxele
				  
				  Na początku LightVoxelBox nie zawiera żadnych LightVoxeli.
				    1. LightVoxelBox zostaje poproszony o utworzenie istotnych voxeli
					     tzn skrajnych, opisujących bryłę, tych, które są widoczne
					   1.1 Sprawdz czy dla danego voxela (x,y,z) wartosc h=height_array[x],[y] spelnia zaleznosc z<=h    - to da wszystkie voxele bedace czescia bryly
					   1.2 Umiesc LightVoxele bedace czescia bryly w 3-wymiarowej tablicy voxel_space 
					       gdzie wspolrzedne danego voxela odpowiadaja wspolrzednym, pod ktorymi jest umiesczony w tablicy - dzieki temu beda mogly sie odnoscic do siebie na wzajem
					   1.3 Popros kazdy z nich aby sprawdzil czy jest voxelem opisującym
						   dowie sie tego sprawdzajac czy ktorakolwiek z jego scianek bedzie widoczna, tzn
						   czy nie jest prawda, ze przylegają do niego innego voxele z kazdej z 6 stron (za pomoca atablicy voxel_space)
						   jesli sie okaze ze nei jest skrajny to oznaczy sie jako do usuniecia
					   1.4 Usun nieskrajne voxele - teraz voxel_space zawiera tylko LightVoxele opisujace bryle
				    2. Kazdy LightVoxel generuje lokalny opis trojkatow potrzebnych do przedstawienai jego widocznych scian
					   wazne: tutaj nalezy zaimplementowac wymagania dotyczace kolejnosci punktow w trojkacie (orientacja)
					          jesli to bedzie zrobione dobrze potem wystarczy zmaienic lokalne odnosniki na numery z globalnej listy wierzcholkow
					   note: tutaj chyba najlatwiej bedzie przyjac ze kazdy voxel ma te sama 'orientacje' 
					         tzn jego pierwszy punkt i kolejnosc numerowania odnosza sie do globalnego ukladu wspolrzednych
					  2.1 Sprawdz kazdy z 6 sasiednich voxeli czy zaslaniaja dana sciane
					  2.2 jesli sciana niezaslaniana to opisz trojkaty
					3. Zapytaj kazdy voxel o wspolrzedne jego wierzcholkow i wpisz je na liste
					   jesli wierzcholek juz jest na liscie to nie wpisuj, uzyj istniejacego
					   w zamian powiedz kazdemu voxelowi ktory numer ma kazdy z jego wierzchokow na globalnej liscie
					4. Popros kazdy voxel o wygenerowanie opisu trojkatow na podstawie dostarczonych globalnych numerow punktow
          

# v1
 
Zalozmy ze istnieje obiekt reprezentujacy plik 3mf z pojedyncza przestrzenia
chce moc do niego powiedziec: masz tutaj trojkat o konkretnych wspolrzednych, dodaj go do struktury
 - czy moge to robi niezaleznie jeden po drugim? i za kazdym razem odswierzac zawartosc pliku?
 - moze niech plik zawiera potencjalne wspolrzedne i je uaktywnia po kolei jak je podaje w dziedzinie [x,y,z]

	   no spoko ale one musza byc w konkretnej kolejnosci
	   to tak jakby powiedzeic zmapuj np (1000x1000x100) liczb na kolejne naturalne

		ja ci bede podawal punkty formie [x,y,z] a ty mi powiedz jaki ma numer
		zapamietaj sobie ze o niego pytalem
		wtedy ja sobie spokojnie pracuje w [x,y,z] a ty mi dasz dla kazdego [x,y,z] juz ustalony numer,
		- potem jak bede przechodzil przez wszystkie punkty...
		jak ci dam punkt no to trzeba go wpisac do pliku na pewno, ale:

		    - jak podam ci go z numerem to jak go wcisnac pomiedzy sasiadow bez przeszukiwania calej listy
		      nie wiadomo jaki ma miec numer na liscie, chyba ze juz jest na liscie, a nie chce ci sie szukac
		       - nie no chwila przeciez jak bede mial zwykal liste o danej dlugosci to moge go poprostu wstawic
			 tam gdzie ma byc
		    - nie mozesz go wpisac drugi raz, jesli juz jest na liscie

		tak wlasciwie chcialbym ci dawac tez trojkaty, no a to to samo co dac ci punkty w konkretnej kolejnosci
		moglbym ci tez dac caly mesh troijkatow, no a to to samo co dac ci poprostu worek z trojkatami
		te trojkaty trzeba najpierw jakos utworzyc
		zeby ci ulatwic zadanie, obiecuje ze jak juz do ciebie zadzwonie
		to podam ci je w nastepujacej formie

		    TriangleMesh, ktora w 'triangles' zawiera worek z trojkatami
		    trojkaty w 'vertices' zawieraja obiekty Vertex a te maja wspolrzedne

			jak sobie zobacyzs na trojkat, to Vertexy sa w nim juz w odpowiedniej kolejnosci
			to bardzo wazne, zeby ja zachowac.
			brakuje im jednak globalnego numeru, dzieki ktoremu moglbys od razu wpisac je w odpowiednie miejsce
			 na liscie i praktycznie miec wszystko gotowe
			musialem przeciez wyobrazic sobie cala bryle w glowie w plaszczyznie [x,y,z] w formie trojkatow
			 i zeby opisac te trojkaty musialem podac 3 wartosci [x,y,z] w odpowiedniej kolejnosci

WEJSCIE:
	bitmapa, wejsciowy obraz

	bitmape dosc latwo i szybko przerobie na liste wspolrzednych oraz liste trojkatow
	wystarczy ze budujac proceduralnie bryle zachowam polaczenia miedzy obiektami
	Vertex i Triangle
	    kazdy triangle ma dokladnie 3 vertexy w okreslonej kolejnosci)
		triqangle  jest opisany wylacznei Vertexami i ich kolejnoscia w trojkacie

	    kazdy Vertex moze 'nalezec' do wielu trojkatow
		Vertex jest opisany wspolrzednymi i swoja kolejnoscia w pliku
		najpierw zdefiniuje potrzbne wierzcholki ze wspolrzednymi
		potem zdefiniuje trojkaty na podstawie tych wierzcholkow
		samo zapisanie do pliku to poprostu przejscie przez wszystkie trojkaty
		i wziecie z kazdego vertexow
		 - jesli nie ma jeszcze numeru to nadaj mu kolejny i doodaj vertex do struktury xml
		 - jesli juz ma to znaczy ze zostal wpisany, zignoruj
		 - po przerobieniu 3 vertexow dodaj trojkat do stuktury xml, uzywajak numerow przypisanych wczesniej
		   vertexom
	   
WYJSCIE:
	plik 3mf

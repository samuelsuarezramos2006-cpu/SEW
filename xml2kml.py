# Creador_KML_Etapa.py
# # -*- coding: utf-8 -*-
""""
Crea archivos KML con puntos y líneas a partir de un archivo XML

@version 1.0 
@author: Samuel Suárez Ramos
"""

import xml.etree.ElementTree as ET

class Kml(object):

    def __init__(self):
        """
        Crea el elemento raíz y el espacio de nombres
        """
        self.raiz = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz,'Document')

    def addPlacemark(self,nombre,descripcion,long,lat,alt, modoAltitud):
        """
        Añade un elemento <Placemark> con puntos <Point>
        """
        pm = ET.SubElement(self.doc,'Placemark')
        ET.SubElement(pm,'name').text = nombre
        ET.SubElement(pm,'description').text = descripcion
        punto = ET.SubElement(pm,'Point')
        ET.SubElement(punto,'coordinates').text = '{},{},{}'.format(long,lat,alt)
        ET.SubElement(punto,'altitudeMode').text = modoAltitud

    def addLineString(self,nombre,extrude,tesela, listaCoordenadas, modoAltitud, color, ancho):
        """
        Añade un elemento <Placemark> con líneas <LineString>
        """
        ET.SubElement(self.doc,'name').text = nombre
        pm = ET.SubElement(self.doc,'Placemark')
        ls = ET.SubElement(pm, 'LineString')
        ET.SubElement(ls,'extrude').text = extrude
        ET.SubElement(ls,'tessellation').text = tesela
        ET.SubElement(ls,'coordinates').text = listaCoordenadas
        ET.SubElement(ls,'altitudeMode').text = modoAltitud 

        estilo = ET.SubElement(pm, 'Style')
        linea = ET.SubElement(estilo, 'LineStyle')
        ET.SubElement (linea, 'color').text = color
        ET.SubElement (linea, 'width').text = ancho

    def escribir(self,nombreArchivoKML):
        """
        Escribe el archivo KML con declaración y codificación
        """
        arbol = ET.ElementTree(self.raiz)
        """
        Introduce indentacióon y saltos de línea
        para generar XML en modo texto
        """
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding='utf-8', xml_declaration=True)
    
    def ver(self):
        """
        Muestra el archivo KML. Se utiliza para depurar
        """
        print("\nElemento raiz = ", self.raiz.tag)

        if self.raiz.text != None:
            print("Contenido = "    , self.raiz.text.strip('\n')) 
        else:
            print("Contenido = "    , self.raiz.text)
        
        print("Atributos = "    , self.raiz.attrib)

        for hijo in self.raiz.findall('.//'): 
            print("\nElemento = " , hijo.tag)
            if hijo.text != None:
                print("Contenido = ", hijo.text.strip('\n')) 
            else:
                print("Contenido = ", hijo.text)    
            print("Atributos = ", hijo.attrib)


def cargar_etapa_xml(archivo_xml, kml_obj):
    """
    Lee un archivo XML con los datos de la etapa y añade los 
    Placemarks y LineString correspondientes al objeto KML.
    """
    try:
        arbol = ET.parse(archivo_xml)
    except IOError:
        print('No se encuentra el archivo ', archivo_xml)
        exit()
    except ET.ParseError:
        print("Error procesando en el archivo XML = ", archivo_xml)
        exit()

    root = arbol.getroot()

    ns = {'ns': 'http://www.uniovi.es'}

    nombre_etapa = root.findtext('./ns:nombre', default='Etapa sin nombre', namespaces=ns)
    ciudad_salida = root.findtext('./ns:ciudad_salida', default='', namespaces=ns)
    ciudad_llegada = root.findtext('./ns:ciudad_llegada', default='', namespaces=ns)

    puntos_ruta = []

    salida = root.find('./ns:coordenadas_salida', namespaces=ns)
    if salida != None:
        lat = salida.findtext('./ns:latitud', namespaces=ns)
        lon = salida.findtext('./ns:longitud_geo', namespaces=ns)
        alt = salida.findtext('./ns:altitud', namespaces=ns)
        nombre = "Salida: " + ciudad_salida
        desc = "Salida de la etapa en " + ciudad_salida
        kml_obj.addPlacemark(nombre, desc, lon, lat, alt, 'relativeToGround')
        puntos_ruta.append('{},{},{}'.format(lon, lat, alt))


    hitos = root.findall('./ns:hitos/*', namespaces=ns)
    index = 1
    for hito in hitos:
        lat = hito.findtext('./ns:latitud', namespaces=ns)
        lon = hito.findtext('./ns:longitud_geo', namespaces=ns)
        alt = hito.findtext('./ns:altitud', namespaces=ns)

        if hito.tag.endswith('puerto_montana'):
            nombre_hito = hito.findtext('./ns:nombre_puerto', default='Puerto {}'.format(index), namespaces=ns)
            cat = hito.findtext('./ns:categoria', default='', namespaces=ns)
            desc_hito = "Puerto de Montaña (Categoría: {})".format(cat)
        elif hito.tag.endswith('sprint'):
            nombre_hito = hito.findtext('./ns:nombre_sprint', default='Sprint {}'.format(index), namespaces=ns)
            desc_hito = "Sprint Intermedio"
        else:  # punto_anonimo
            dist = hito.findtext('./ns:distancia', default='', namespaces=ns)
            nombre_hito = "Hito Intermedio {}".format(index)
            if dist:
                desc_hito = "Punto kilométrico {} km".format(dist)
            else:
                desc_hito = "Punto intermedio"

        kml_obj.addPlacemark(nombre_hito, desc_hito, lon, lat, alt, 'relativeToGround')
        puntos_ruta.append('{},{},{}'.format(lon, lat, alt))
        index += 1


    meta = root.find('./ns:coordenadas_meta', namespaces=ns)
    if meta != None:
        lat = meta.findtext('./ns:latitud', namespaces=ns)
        lon = meta.findtext('./ns:longitud_geo', namespaces=ns)
        alt = meta.findtext('./ns:altitud', namespaces=ns)
        nombre = "Meta: " + ciudad_llegada
        desc = "Llegada de la etapa en " + ciudad_llegada
        kml_obj.addPlacemark(nombre, desc, lon, lat, alt, 'relativeToGround')
        puntos_ruta.append('{},{},{}'.format(lon, lat, alt))

    # Trazar la ruta uniéndola
    cadena_coordenadas = "\n".join(puntos_ruta)
    nombre_linea = "Ruta " + nombre_etapa
    kml_obj.addLineString(nombre_linea, "1", "1",
                          cadena_coordenadas, 'relativeToGround',
                          '#ff0000ff', "5")


def main():
    print(Kml.__doc__)

    """Prueba unitaria de la clase Kml alimentada por un archivo XML"""
    archivo_xml = "etapaEsquema.xml"
    archivo_kml = "etapa.kml"

    nuevoKML = Kml()
    
    cargar_etapa_xml(archivo_xml, nuevoKML)
    
    """Visualización del KML creado"""
    nuevoKML.ver()
    
    """Creación del archivo en formato KML"""
    nuevoKML.escribir(archivo_kml)
    print("\nCreado el archivo: ", archivo_kml)


if __name__ == "__main__":
    main()
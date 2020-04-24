from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QApplication, QLineEdit, QMessageBox
import webbrowser
import flightradar24

airplane_id = ''
api_key = "AIzaSyB3FBBIpx0pFY_yeO6xUOdHGFmX6_zeN9s"

def getmaphtml(flight_id=airplane_id):
    s = str("")
    if flight_id == '':
        s = str("""<html><head><style>h3{margin-top: 20px;}</style></head><body><h3>Plane not selected</h3></body></html>""")
    else:
        fr = flightradar24.Api()

        flight = fr.get_flight(flight_id) # getting data like flight.json
        # print(flight)
        flightData = flight["result"]["response"]["data"]
        if flightData != None:
            livePlanes = [plane for plane in flightData if plane["status"]["live"]]
            livePlanesId = [plane["identification"]["id"] for plane in livePlanes]
            livePlanesAirline = [plane["airline"]["code"]["icao"] for plane in livePlanes]
            # print(livePlanes)
            print("Live planes: " + str(len(livePlanes)))

            if len(livePlanes) > 0:
                print("Plane id: " + livePlanesId[0])
                print("Airline: " + livePlanesAirline[0])
                flights = fr.get_flights(livePlanesAirline[0]) # getting data like flights.json
                # print(flights)
                planeLat = flights[livePlanesId[0]][1]
                planeLng = flights[livePlanesId[0]][2]
                planeAngle = flights[livePlanesId[0]][3]
                planeAltitude = flights[livePlanesId[0]][4]
                planeSpeed = flights[livePlanesId[0]][5]
                print("Latitude: " + str(planeLat) + " Longitude: " + str(planeLng) + " Speed: " + str(
                    round(planeSpeed * 1.852)) + "(km/h) Altitude: " + str(round(planeAltitude / 3281, 3)) + "km")

                s = str("""<html>
                  <head>
                    <style>
                      /* Set the size of the div element that contains the map */
                      #map {
                        height: 100%;  /* The height is 400 pixels */
                        width: 100%;  /* The width is the width of the web page */
                       }
                    </style>
                  </head>
                  <body>
                    <!--The div element for the map -->
                    <div id="map"></div>
                    <script>
                // Initialize and add the map
                function initMap() {
                  // The location of airplane
                  var plane = {lat: """ + str(planeLat) + """, lng: """ + str(planeLng) + """};
                  // The map, centered at plane
                  var map = new google.maps.Map(
                      document.getElementById('map'), {zoom: 5, center: plane});
                  // The marker, positioned at plane
                  var icon = {
                    // url: "https://ru.seaicons.com/wp-content/uploads/2015/08/Airplane-Top-Red-icon.png", // url
                    path: 'M 22 16 v -2 l -8.5 -5 V 3.5 C 13.5 2.67 12.83 2 12 2 s -1.5 0.67 -1.5 1.5 V 9 L 2 14 v 2 l 8.5 -2.5 V 19 L 8 20.5 L 8 22 l 4 -1 l 4 1 l 0 -1.5 L 13.5 19 v -5.5 L 22 16 Z',
                    fillColor: '#F00',
                    fillOpacity: 1,
                    // scaledSize: new google.maps.Size(64, 64), // scaled size
                    // origin: new google.maps.Point(0,0), // origin
                    anchor: new google.maps.Point(11, 8), // anchor
                    rotation: """ + str(planeAngle) + """,
                    scale: 1
                };
    
                  var marker = new google.maps.Marker({position: plane, map: map, icon: icon, title: "Plane is here!", label: "Plane"});
                }
                    </script>
                    <script async defer
                    src="https://maps.googleapis.com/maps/api/js?key=""" + str(api_key) + """&callback=initMap">
                    </script>
                  </body>
                </html>""")
            else:
                s = str("""<html><head><style>h3{margin-top: 20px;}</style></head><body><h3>Plane is offline</h3></body></html>""")
        else:
            s = str("""<html><head><style>h3{margin-top: 20px;}</style></head><body><h3>Can't find plane</h3></body></html>""")
    return s

class MainWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.title = 'Flightradar24 parser by DroidCatRu'
        self.setWindowTitle(self.title)
        self.resize(700, 500)
        self.view = QWebEngineView(self)
        self.setpage()

        self.textbox = QLineEdit(self)
        self.textbox.move(20, 10)
        self.textbox.resize(280, 20)

        btn = QPushButton('Показать рейс', self)
        btn.resize(btn.sizeHint())
        btn.move(300, 10)

        grid = QGridLayout()
        grid.addWidget(self.view)
        self.setLayout(grid)
        btn.clicked.connect(self.clikbtn)  # Кнопка обновления карты
        self.show()

    def setpage(self, id=airplane_id):
        mypage = MyPage(self.view)
        self.view.setPage(mypage)
        s = getmaphtml(id)
        mypage.setHtml(s)

    def clikbtn(self):
        QMessageBox.question(self, 'Не увлекайтесь', "Стоимость одной загрузки карты: 0,46 рубля. Студенты тоже есть хотят. +79093636316 (сбер)", QMessageBox.Ok, QMessageBox.Ok)
        id = self.textbox.text()
        self.setpage(id)
        self.view.reload()


class MyPage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.in_window = False

    def createWindow(self, type):
        self.in_window = True
        return self

    def acceptNavigationRequest(self, QUrl, type, isMainFrame):
        url_string = QUrl.toString()
        # print(type, isMainFrame, QUrl)
        if self.in_window and type == 2:
            webbrowser.open(url_string)
            self.in_window = False
            s = getmaphtml(airplane_id)
            self.setHtml(s)
        return True


if __name__ == '__main__':
    app = None
    if not QApplication.instance():
        app = QApplication([])
    dlg = MainWindow()
    if app:
        app.exec_()

#include <CurieIMU.h>
#include <CurieBLE.h>
#include <MadgwickAHRS.h>

int flag=0;
Madgwick filter;
unsigned long microsPerReading, microsPrevious;
float accelScale, gyroScale;

int aix, aiy, aiz;
int gix, giy, giz;
float ax, ay, az;
float gx, gy, gz;
int roll, pitch, heading;
unsigned long microsNow;
unsigned char arr[6] = { 0, 0, 0, 0, 0, 0 };

//BLEPeripheral midiDevice; // create peripheral instance
BLEService midiSvc("03B80E5A-EDE8-4B33-A751-6CE34EC4C700"); // create service

//create switch characteristic and allow remote device to read and write
//BLECharacteristic midiChar("7772E5DB-3868-4112-A1A9-F2669D106BF3",  BLEWrite | BLEWriteWithoutResponse | BLENotify | BLERead,5);
BLECharacteristic midiChar("7772E5DB-3868-4112-A1A9-F2669D106BF3", BLERead | BLENotify, 6);

void setup() {
  Serial.begin(115200);
  // start the IMU and filter
  CurieIMU.begin();
  CurieIMU.setGyroRate(25);
  CurieIMU.setAccelerometerRate(25);
  filter.begin(25);
  // Set the accelerometer range to 2G
  CurieIMU.setAccelerometerRange(2);
  // Set the gyroscope range to 250 degrees/second
  CurieIMU.setGyroRange(25);
  // initialize variables to pace updates to correct rate
  microsPerReading = 1000000 / 25;
  microsPrevious = micros();

  /*BLESetup();
  BLE.advertise();// advertise the service
  Serial.println(("Bluetooth device active, waiting for connections..."));*/
}

void BLESetup()
{
  BLE.begin();
  BLE.setLocalName("Auxren");      // set the local name peripheral advertises
  BLE.setAdvertisedServiceUuid(midiSvc.uuid());     // set the UUID for the service this peripheral advertises
  midiSvc.addCharacteristic(midiChar);    // add service and characteristic
  BLE.addService(midiSvc);

  BLE.setEventHandler(BLEConnected, midiDeviceConnectHandler);     
  BLE.setEventHandler(BLEDisconnected, midiDeviceDisconnectHandler);

  // assign event handlers for characteristic
  //midiChar.setEventHandler(BLEWritten, midiCharacteristicWritten);
  // set an initial value for the characteristic
  //midiChar.setValue(midiData, 5);
}

void loop() {
  //if(flag){
    //Serial.println("1");
    //BLE.poll();
    //Serial.println("2");
  microsNow = micros();  // check if it's time to read data and update the filter
  if (microsNow - microsPrevious >= microsPerReading) {

    // read raw data from CurieIMU
    CurieIMU.readMotionSensor(aix, aiy, aiz, gix, giy, giz);
    Serial.print(aix);
    Serial.print(" ");
    Serial.print(aiy);
    Serial.print(" ");
    Serial.print(aiz);
    Serial.print(" ");
    Serial.print(gix);
    Serial.print(" ");
    Serial.print(giy);
    Serial.print(" ");
    Serial.println(giz);

    /*
    // convert from raw data to gravity and degrees/second units
    ax = convertRawAcceleration(aix);
    ay = convertRawAcceleration(aiy);
    az = convertRawAcceleration(aiz);
    gx = convertRawGyro(gix);
    gy = convertRawGyro(giy);
    gz = convertRawGyro(giz);
    
    // update the filter, which computes orientation
    filter.updateIMU(gx, gy, gz, ax, ay, az);
    //Serial.println("4");

    // print the heading, pitch and roll
    roll   = (filter.getRoll()  + 180);// * 100;
    pitch  = (filter.getPitch() + 180);// * 100;
    heading= (filter.getYaw());// * 100);

    
    Serial.print(heading);
    Serial.print(" ");
    Serial.print(pitch);
    Serial.print(" ");
    Serial.println(roll);*/

    microsPrevious = microsPrevious + microsPerReading;     // increment previous time, so we keep proper pace

    /*arr[0] = heading & 0xFF;
    arr[1] = heading >> 8;
    arr[2] = pitch & 0xFF;
    arr[3] = pitch >> 8;
    arr[4] = roll & 0xFF;
    arr[5] = roll >> 8;
    //Serial.println("5");
    midiChar.setValue(arr, 6);
    //Serial.println("6");*/
    }
  //}
}

float convertRawAcceleration(int aRaw) {
  // since we are using 2G range  // -2g maps to a raw value of -32768  // +2g maps to a raw value of 32767
  float a = (aRaw * 2.0) / 32768.0;  return a;
}

float convertRawGyro(int gRaw) {
  // since we are using 250 degrees/seconds range  // -250 maps to a raw value of -32768  // +250 maps to a raw value of 32767
  float g = (gRaw * 250.0) / 32768.0;  return g;
}

void midiDeviceConnectHandler(BLEDevice central) {
  // central connected event handler
  Serial.print("Connected event, central: ");
  Serial.println(central.address());
  flag=1;
}

void midiDeviceDisconnectHandler(BLEDevice central) {
  // central disconnected event handler
  Serial.print("Disconnected event, central: ");
  Serial.println(central.address());
  flag=0;
}

void midiCharacteristicWritten(BLEDevice central, BLECharacteristic characteristic) {
// central wrote new value to characteristic, update LED
  Serial.print("Characteristic event, written: ");
}

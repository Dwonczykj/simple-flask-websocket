import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or simply save your changes to "hot reload" in a Flutter IDE).
        // Notice that the counter didn't reset back to zero; the application
        // is not restarted.
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();

  static String appHost = '127.0.0.1';
  static String appPort = '8444';
  static String apiUrl = 'http://$appHost:$appPort/';
  static String wsUrl = 'ws://$appHost:$appPort/websocket';
  static String socketIoUrl = 'ws://$appHost:$appPort/socket.io';

  // final _channel = WebSocketChannel.connect(Uri.parse(
  //         wsUrl) // https://blog.postman.com/introducing-postman-websocket-echo-service/
  //     );

  final _channel = SocketService()
    ..createSocketConnection(
        apiUrl // https://blog.postman.com/introducing-postman-websocket-echo-service/
        );

  final _socketioNamespaceChannel = SocketService()
    ..createSocketConnection(
        socketIoUrl // https://blog.postman.com/introducing-postman-websocket-echo-service/
        );

  List<dynamic> items = <String>[''];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Form(
              child: TextFormField(
                controller: _controller,
                decoration: const InputDecoration(labelText: 'Send a message'),
              ),
            ),
            const SizedBox(height: 24),
            Container(
              height: 300,
              alignment: Alignment.center,
              child: StreamBuilder(
                stream: _channel.stream,
                builder: (context, snapshot) {
                  if (snapshot.hasData) {
                    items.add(snapshot.data);
                    //print every second: [0] then [0,1] then [0,1,2] ...
                  }
                  return ListView(
                    children: items
                        .sublist(math.max(0, items.length - 3))
                        .map((item) => ListTile(
                              title: Text(item.toString()),
                            ))
                        .toList(),
                  );
                },
              ),
            ),
            const SizedBox(height: 24),
            Text(
                'Socket endpoint: $socketIoUrl is ${_channel.connectionStatus} with EIO: ${_channel.protocol}')
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _sendMessage,
        tooltip: 'Send message',
        child: const Icon(Icons.send),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }

  void _sendMessage() {
    if (_controller.text.isNotEmpty) {
      // _channel.sink
      //     .add(jsonEncode({'type': 'message', 'data': _controller.text}));
      _channel.emit('message', _controller.text);
      _socketioNamespaceChannel.emit(
          'message', '${_controller.text} on socket.io nsp channel');
      _controller.clear();
    }
  }

  @override
  void dispose() {
    _channel.sink.close();
    _controller.dispose();
    super.dispose();
  }
}

class SocketService {
  final _streamController = StreamController<dynamic>();

  get stream => _streamController.stream;

  get sink => _streamController.sink;

  io.Socket? socket;

  String get protocol => socket?.io.uri ?? 'N/A';

  String get connectionStatus =>
      ((socket?.connected ?? false) ? 'connected' : null) ?? 'diconnected';

  createSocketConnection(String socketIoUrl) {
    var _socket = io.io(socketIoUrl, {
      'transports': ['websocket'],
      'autoConnect': true,
    })
      ..on('connect', (_) {
        print('connected to socketio from flutter SocketService');
      })
      ..on('disconnect', (_) {
        print('disconnected from socketio in flutter SocketService');
      })
      ..on('message', _msgEventHandler);

    socket = _socket;

    _socket.onConnect((_) {
      print('connect');
      _socket.emit('message', 'test message from Joey D');
      print('Connected Status: ${_socket.connected}');
      print('Socket ID: ${_socket.id}');
    });

    _socket.on('event', (data) => print(data));
    _socket.onDisconnect((_) => print('disconnect'));
    _socket.on('fromServer', (_) => print(_));

    //socket.off('active_bands');
    // socket?.onConnect((data) {
    //   socket?.emit('message', {'some': 'thing'});
    // });
    // socket?.onConnectError((data) => print(data));
    _socket.emit('add_band', {'name': 'fluttertutorial'});
    _socket.on('active_bands', _eventHandler);
    _socket.on('message', _msgEventHandler);
  }

  _socketStatus(dynamic status) {
    print('socketio status: $status');
  }

  // SocketIO? socketIO;

  // createSocketConnection2(String url) {
  //   socketIO = SocketIOManager().createSocketIO(url, "/chat",
  //       query: "userId=21031", socketStatusCallback: _socketStatus);

  //   //call init socket before doing anything
  //   socketIO!.init();

  //   //subscribe event
  //   socketIO!.subscribe("message", _msgEventHandler);

  //   //connect socket
  //   socketIO!.connect();
  // }

  void emit(String event, [dynamic data = const <String, dynamic>{}]) {
    socket?.emit(event, data);
  }

  void _eventHandler(dynamic object) {
    print(object);
    _streamController.add(object);
  }

  void _msgEventHandler(dynamic object) {
    print('message event handler: $object');
    _streamController.add(object);
  }
}

// App.tsx
import React from 'react';
import { Text, StyleSheet, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { HomeScreen } from './screens/HomeScreen';
import { DirectSearchScreen } from './screens/DirectSearchScreen';
import { NearestParkingScreen } from './screens/NearestParkingScreen';

const Stack = createStackNavigator();

// Custom gradient-style header title component
const GradientHeaderTitle = ({ title }: { title: string }) => (
  <Text style={styles.gradientHeaderText}>{title}</Text>
);

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1a0025',
            elevation: 8,
            shadowColor: '#8B5FBF',
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: 0.3,
            shadowRadius: 8,
          },
          headerTintColor: '#fff',
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ 
            headerTitle: () => <GradientHeaderTitle title="Parking Spotter" />
          }}
        />
        <Stack.Screen 
          name="DirectSearch" 
          component={DirectSearchScreen}
          options={{ 
            headerTitle: () => <GradientHeaderTitle title="Search Cameras" />
          }}
        />
        <Stack.Screen 
          name="NearestParking" 
          component={NearestParkingScreen}
          options={{ 
            headerTitle: () => <GradientHeaderTitle title="Nearest Parking" />
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  gradientHeaderText: {
    fontSize: 18,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    color: '#FFB366',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 6,
    letterSpacing: 2,
    textTransform: 'uppercase',
    transform: [{ skewX: '-3deg' }],
  },
});
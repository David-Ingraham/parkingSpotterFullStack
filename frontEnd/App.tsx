// App.tsx
import React from 'react';
import { Text, StyleSheet } from 'react-native';
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#8B5FBF',
    textShadowColor: 'rgba(139, 95, 191, 0.5)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
    letterSpacing: 0.5,
  },
});